from django.shortcuts import render

from django.views.generic import ListView, DetailView, CreateView 
from .models import Equipment, Lending, Log
from django.urls import reverse_lazy
from django.shortcuts import redirect

from django.utils import timezone

#ログインの制御系
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class EquipmentList(LoginRequiredMixin, ListView):
    template_name = 'equip_app/list.html'
    login_url = '/login/'

    model = Equipment
    context_object_name = 'equip_list'
    queryset = Equipment.objects.order_by('category__main_category', 'management_num')
    paginate_by = 30

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["title"] = "一覧"
        return context

class EquipmentDetail(LoginRequiredMixin, DetailView):
    template_name = 'equip_app/detail.html'
    model = Equipment
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "詳細"
        return context
    
class CreateLend(LoginRequiredMixin, CreateView):
    template_name = 'equip_app/create.html'
    model = Lending
    fields = ('item_name', 'note',)
    login_url = '/login/'
    success_url = reverse_lazy('lend_create')

    def get_context_data(self, **kwargs):
        kwargs['equip_list'] = Equipment.objects.order_by('category__main_category', 'management_num')
        kwargs["title"] = "貸出画面"
        return super(CreateLend, self).get_context_data(**kwargs)
    
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        self.updatelog(obj)
        kwargs = self.get_context_data()
        kwargs['success'] = "貸出に成功しました"
        kwargs['success_item'] = str(obj.item_name)
        kwargs['success_lend_date'] = obj.lend_date
        kwargs['success_return_date'] = obj.return_date
        kwargs['success_lend_span'] = str(obj.lend_span)
        return self.render_to_response(kwargs)
 
    def form_invalid(self, form):
        kwargs = self.get_context_data()
        kwargs['error'] = "貸出に失敗しました"
        return self.render_to_response(kwargs)

    def updatelog(self, obj):
        log_obj, created = Log.objects.get_or_create(item_name = obj.item_name)
        log_obj.available = "不可"
        log_obj.times += 1
        log_obj.now_user = obj.user
        log_obj.history = str(F"<貸出>,{obj.user},{timezone.localtime(obj.lend_date).strftime('%Y/%m/%d %H:%M:%S')},{timezone.localtime(obj.return_date).strftime('%Y/%m/%d %H:%M:%S')},{obj.lend_span},{obj.note}\n") + str(log_obj.history)
        log_obj.save()

    """
    貸出を開始する時
    ・Lendingモデルにデータを追加
    ・Logモデルのavailable, now_userを変更
    """
    ##参考サイトなど
    #・https://zenn.dev/miyaji26/articles/b1a98c13c0bab4 ロッキングについて
    #https://yu-nix.com/blog/2021/7/31/django-create-view/#Django%E3%81%AE%E8%8F%AF%E9%BA%97%E3%81%AA%E3%82%8BCreateView%E3%81%AE%E4%BD%BF%E3%81%84%E6%96%B9
    #https://awesome-linus.com/2019/04/05/django-get-login-user/
    #https://qiita.com/yukiya285/items/32fb96c1bd760b594974
    #https://note.com/mihami383/n/n610b5395877e
    #https://qiita.com/onishi_820/items/c9418f95a8e4e828dfc4
    #https://hombre-nuevo.com/python/python0059/
    
class LendList(ListView, LoginRequiredMixin):
    template_name = 'equip_app/lend.html'
    model = Lending
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lend_list'] = Lending.objects.filter(user = self.request.user).all()
        context["title"] = "貸出中一覧"
        return context

    #http://www.umadura.com/?p=2548#get_context_data

    def post(self, request, *args, **kwargs):
        try:
            lend_obj = Lending.objects.get(pk = request.POST["lend_name"])
            log_obj = Log.objects.get(item_name = request.POST["item_name"])
        except:
            self.kwargs['error'] = "予期しない動作です"
        try:
            if lend_obj.user == self.request.user:
                lend_obj = Lending.objects.get(pk = request.POST["lend_name"])
                log_obj = Log.objects.get(item_name = request.POST["item_name"])
                lend_obj.delete()
                return_date = self.updatelog(log_obj)
                self.kwargs['success'] = "返却に成功しました"
                self.kwargs['success_item'] = str(lend_obj.item_name)
                self.kwargs['success_return_date'] = return_date
            else:
                self.kwargs['hard_error'] = "不正な返却な可能性があります"
        except:
            pass
        self.kwargs["title"] = "貸出中一覧"
        self.kwargs['lend_list'] = Lending.objects.filter(user = self.request.user).all()
        return render(request, self.template_name, context=self.kwargs)

    def updatelog(self, obj):
        return_date = timezone.localtime(timezone.now())
        log_obj, created = Log.objects.get_or_create(item_name = obj.item_name)
        if created == True:
            log_obj.times = 1
        log_obj.previous_user = log_obj.now_user
        log_obj.now_user = None
        log_obj.history = str(F"<返却>,{self.request.user},{return_date.strftime('%Y/%m/%d %H:%M:%S')}\n") + str(log_obj.history)

        log_obj.available = "可"
        log_obj.save()
        return return_date

    """
    返却をするとき
    ・Lendingモデルからデータを削除
    ・Logモデルのhistoryに追記

    #https://selfnote.work/20190929/programming/django/django-shoppingcart-7/
    """
"""
メモ
print([hasattr(i, 'note') for i in context['equip_list']])
print([hasattr(i, 'logmodel') for i in context['equip_list']])
print([hasattr(i, 'related_itemname') for i in context['equip_list']])
print([hasattr(i, 'related_itemname.times') for i in context['equip_list']])#"related_itemname.times"として存在するわけではないから?
print([i.related_itemname.times for i in context['equip_list'] if hasattr(i, 'related_itemname') ])

[True, True, True, True, True, True, True, True]
[False, False, False, False, False, False, False, False]
[True, False, False, False, False, False, False, False]
[False, False, False, False, False, False, False, False]
[2]
"""