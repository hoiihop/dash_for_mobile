from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, reverse
from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import View, ListView, CreateView, DeleteView, DetailView, UpdateView
from django.views.generic.base import RedirectView

from .forms import *
from .models import Promotion


# class MainView(LoginRequiredMixin, View):
#     def get(self, request):
#         return render(request, 'mobile_api/index.html')


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm


class MobileDeviceList(LoginRequiredMixin, ListView):
    model = MobileDevice
    template_name = 'mobile_api/mobile_device_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['device_errors'] = MobileDevice.objects.filter(user_id=0).count()

        return context


class MobileDeviceUpdate(LoginRequiredMixin, UpdateView):
    model = MobileDevice
    form_class = MobileDeviceForm
    template_name = 'mobile_api/mobile_device_update.html'

    def get_success_url(self):
        return reverse("mobile_device_update", kwargs={"pk": self.kwargs['pk']})


class MobileDeviceRepair(LoginRequiredMixin, RedirectView):
    pattern_name = 'mobile_device_list_view'

    # Delete all data where user_id=0
    def get_redirect_url(self, *args, **kwargs):
        mobile_device_errors = MobileDevice.objects.filter(user_id=0)
        mobile_device_errors.delete()
        return super().get_redirect_url(*args, **kwargs)


class DeleteSelectMobileDevice(LoginRequiredMixin, RedirectView):
    pattern_name = 'mobile_device_list_view'

    def get_redirect_url(self, *args, **kwargs):
        user = kwargs.pop('user')
        MobileDevice.objects.filter(user_id=user).delete()

        return super().get_redirect_url(*args, **kwargs)


class MobileDeviceDelete(LoginRequiredMixin, DeleteView):
    model = MobileDevice
    success_url = reverse_lazy('mobile_device_list_view')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class FeedbackList(LoginRequiredMixin, ListView):
    model = Feedback
    template_name = 'mobile_api/feedback_list.html'


class FeedbackUpdate(LoginRequiredMixin, View):
    def get(self, request, pk):
        feed_img = ''
        feedback = get_object_or_404(Feedback, pk=pk)

        try:
            user_id = feedback.user_id
        except ObjectDoesNotExist:
            user_id = None

        if feedback.photo:
            feed_img = feedback.phot

        if feedback.answer_id:
            return render(request, 'mobile_api/feedback_update.html', context={
                'object': feedback,
                'user': user_id,
                'photo': feed_img,
                'form': None
            })
        else:
            return render(request, 'mobile_api/feedback_update.html', context={
                'object': feedback,
                'user': user_id,
                'photo': feed_img,
                'form': FeedbackForm()
            })

    def post(self, request, pk):
        feedback = Feedback.objects.get(pk=pk)
        form = FeedbackForm(request.POST)

        if form.is_valid():
            content = form.cleaned_data['content']

            new_msg = Message.objects.create(
                user_id=feedback.user_id,
                pre_title=content[:255],
                title='Служба підтримки UPG',
                content=content
            )
            feedback.answer_id = new_msg
            feedback.save()

            return redirect('feedback_update', feedback.id)


class PushMessageList(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mobile_api/push_list.html'


## VERSION 1
# class PushMessageCreate(View):
#     def get(self, request):
#         return render(request, 'mobile_api/push_create_form.html', context={            
#             'form': NewPushMessageForm()
#         })

#     def post(self, request):
#         form = NewPushMessageForm(request.POST)

#         if form.is_valid():           
#             form.save()
#             return redirect('push_list')

#         return render(request, 'mobile_api/push_create_form.html', context={
#             'form': form
#         })


## VERSION 2
class PushMessageCreate(LoginRequiredMixin, CreateView):
    model = Message
    form_class = NewPushMessageForm
    template_name = 'mobile_api/push_create_form.html'

    def get_success_url(self):
        return reverse('push_list')


class NewsList(LoginRequiredMixin, ListView):
    model = News
    template_name = 'mobile_api/news_promotions_list.html'


class NewsDetail(LoginRequiredMixin, DetailView):
    model = News

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context['object']
        context['news_en'] = NewsEn.objects.get(news=obj)
        context['news_ru'] = NewsRu.objects.get(news=obj)
        context['news_uk'] = NewsUk.objects.get(news=obj)
        context['news_img'] = NewsImg.objects.filter(news=obj, resolution_id=2)

        return context


class NewsCreate(LoginRequiredMixin, View):
    # template_name = 'mobile_api/news_create_form.html'    

    def get(self, request):
        print(NewsForm().__class__.__name__)
        return render(request, 'mobile_api/news_create_form.html', context={
            'f_news': NewsForm(),
            'f_news_en': NewsEnForm(),
            'f_news_ru': NewsRuForm(),
            'f_news_uk': NewsUkForm()
        })

    def post(self, request):
        f_news = NewsForm(request.POST)
        f_news_en = NewsEnForm(request.POST)
        f_news_ru = NewsRuForm(request.POST)
        f_news_uk = NewsUkForm(request.POST)
        if all((f_news.is_valid(), f_news_en.is_valid(), f_news_ru.is_valid(), f_news_uk.is_valid())):
            f_news_saved = f_news.save()

            f_news_en_saved = f_news_en.save(commit=False)
            f_news_en_saved.news = f_news_saved
            f_news_en_saved.save()

            f_news_ru_saved = f_news_ru.save(commit=False)
            f_news_ru_saved.news = f_news_saved
            f_news_ru_saved.save()

            f_news_uk_saved = f_news_uk.save(commit=False)
            f_news_uk_saved.news = f_news_saved
            f_news_uk_saved.save()

            return redirect('news_detail', f_news_saved.id)

        return render(request, 'mobile_api/news_create_form.html', context={
            'f_news': f_news,
            'f_news_en': f_news_en,
            'f_news_ru': f_news_ru,
            'f_news_uk': f_news_uk
        })


# class NewsEdit(View):
#     prefix = get_prefix()

#     def get(self, request, pk): 

#         news = News.objects.get(pk=pk)

#         f_news = NewsForm(instance=news)
#         news_en = NewsEn.objects.get(news=news)
#         f_news_en = NewsEnForm(instance=news_en)
#         news_ru = NewsRu.objects.get(news=news)
#         f_news_ru = NewsRuForm(instance=news_ru)
#         news_uk = NewsUk.objects.get(news=news)
#         f_news_uk = NewsUkForm(instance=news_uk)
#         news_img = NewsImg.objects.filter(news=news)

#         f_news_img = [NewsImgForm(instance=i, prefix='{}_{}'.format(i.lang_abbr.lang_abbr, i.resolution_id)) for i in news_img]

#         print(self.prefix)


#         return render(request, 'mobile_api/news_edit_form.html', context={
#             'f_news': f_news,
#             'f_news_en': f_news_en,            
#             'f_news_ru': f_news_ru,            
#             'f_news_uk': f_news_uk,
#             'f_news_img': f_news_img,
#             'prefix_list': self.prefix
#         })

#     def post(self, request, pk):
#         news = News.objects.get(pk=pk)
#         f_news = NewsForm(request.POST, instance=news)
#         news_en = NewsEn.objects.get(news=news)
#         f_news_en = NewsEnForm(request.POST, instance=news_en)
#         news_ru = NewsRu.objects.get(news=news)
#         f_news_ru = NewsRuForm(request.POST, instance=news_ru)
#         news_uk = NewsUk.objects.get(news=news)
#         f_news_uk = NewsUkForm(request.POST, instance=news_uk)
#         news_img = NewsImg.objects.filter(news=news)
#         f_news_img = [NewsImgForm(request.POST, instance=i, prefix='{}_{}'.format(i.lang_abbr.lang_abbr, i.resolution_id)) for i in news_img]

#         print(f_news_img)

#         if '_cancel' not in request.POST:
#             if all((f_news.is_valid(), f_news_en.is_valid(), f_news_ru.is_valid(), f_news_uk.is_valid(), [i.is_valid() for i in f_news_img])):
#                 f_news_saved = f_news.save()

#                 f_news_en_saved = f_news_en.save(commit=False)
#                 f_news_en_saved.news = f_news_saved
#                 f_news_en_saved.save()

#                 f_news_ru_saved = f_news_ru.save(commit=False)
#                 f_news_ru_saved.news = f_news_saved
#                 f_news_ru_saved.save()

#                 f_news_uk_saved = f_news_uk.save(commit=False)
#                 f_news_uk_saved.news = f_news_saved
#                 f_news_uk_saved.save()            

#                 for img in f_news_img:
#                     f_news_img_saved = img.save(commit=False)
#                     f_news_img_saved.news = f_news_saved
#                     f_news_img_saved.save()                     

#         return redirect('news_detail', news.id)

class NewsEdit(LoginRequiredMixin, View):
    def get(self, request, pk):
        news = News.objects.get(pk=pk)

        f_news = NewsForm(instance=news)

        query_news_en = NewsEn.objects.get(news=news)
        query_news_ru = NewsRu.objects.get(news=news)
        query_news_uk = NewsUk.objects.get(news=news)

        query_news_img_en = NewsImg.objects.filter(news=news).filter(lang_abbr='en')
        query_news_img_ru = NewsImg.objects.filter(news=news).filter(lang_abbr='ru')
        query_news_img_uk = NewsImg.objects.filter(news=news).filter(lang_abbr='uk')

        f_news_en = LangImgNewsForm(lang_query=query_news_en, img_query=query_news_img_en, language='en')
        f_news_ru = LangImgNewsForm(lang_query=query_news_ru, img_query=query_news_img_ru, language='ru')
        f_news_uk = LangImgNewsForm(lang_query=query_news_uk, img_query=query_news_img_uk, language='uk')

        return render(request, 'mobile_api/news_edit_form.html', context={
            'f_news': f_news,
            'f_news_en': f_news_en,
            'f_news_ru': f_news_ru,
            'f_news_uk': f_news_uk
        })

    def post(self, request, pk):
        news = News.objects.get(pk=pk)
        f_news_uk = LangImgNewsForm(request.POST, request.FILES)
        print(f_news_uk.fields['preview_img_url_0'].label)

        return redirect('news_detail', news.id)


class NewsDelete(LoginRequiredMixin, DeleteView):
    model = News
    success_url = reverse_lazy('news_list_view')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class PromotionsList(LoginRequiredMixin, ListView):
    template_name = 'mobile_api/news_promotions_list.html'
    queryset = get_list_or_404(Promotion)
