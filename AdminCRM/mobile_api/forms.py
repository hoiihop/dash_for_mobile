from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import MobileDevice,Feedback, Message, News, NewsEn, NewsRu, NewsUk, NewsImg

CHOICES = (
            (0,'Не активен'),
            (1,'Активен'),
            (2,'Заблокирован')
        )

STATUS = (
    (True, 'Published'),
    (False, 'Not Published')
)

LANGUAGE = ['en', 'ru', 'uk'] 
# (
#     ('en', 'English'),
#     ('ru', 'Русский'),
#     ('uk', 'Українська')
# )

# RESOLUTION = [0, 1, 2, 3]

RESOLUTION = {
    0: '480*360',
    1: '768*600',
    2: '1080*900',
    3: '1440*1300'
}


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Логин'
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Пароль'
    }))


class MobileDeviceForm(forms.ModelForm):
    class Meta:
        model = MobileDevice
        fields = ['status']

        widgets = {
            'status': forms.RadioSelect(choices=CHOICES, attrs={'class': 'flat'})            
        }

    def clean(self):        
        status = self.cleaned_data.get('status')        
        if status == 1:
            query = MobileDevice.objects.filter(phone_number=self.instance.phone_number, status=1)
            
            if (query):
                raise forms.ValidationError('Этот номер уже активен')
        

class FeedbackForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'style': 'width:50%'
    }))
   

# class NewPushMessageForm(forms.Form):
#     title = forms.CharField(max_length=255, widget=forms.TextInput(), label='Заголовок')
#     content = forms.CharField(max_length=4096, label='Сообщение', widget=forms.Textarea(attrs={
#         'class': 'form-control',
#         'style': 'width:100%'
#     }))
    
#     users_phone = forms.ModelMultipleChoiceField(
#         queryset=MobileDevice.objects.filter(status=1, token__isnull=False),
#         label='Номера телефонов',
#             widget=forms.SelectMultiple(attrs={
#                 'class': 'select2_multiple form-control',
#                 'style': 'height:300px'
#             })
#     )

#     def save(self):        
#         content = self.cleaned_data.get('content')
        
#         for user_id in self.cleaned_data.get('users_phone'):            
#             new_msg = Message.objects.create(
#                 user_id=user_id,
#                 pre_title=content[:255],
#                 title=self.cleaned_data.get('title'),
#                 content=content
#             )         

class NewPushMessageForm(forms.ModelForm):
    user_id = forms.ModelMultipleChoiceField(
        queryset=MobileDevice.objects.filter(status=1, token__isnull=False),
        label='Номера телефонов',
        widget=forms.SelectMultiple(attrs={
            'class': 'select2_multiple form-control',
            'style': 'height:300px'
        })
    )

    class Meta:
        model = Message
        fields = ['title', 'content']

        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'style': 'width:100%'
            })
        }

    def __init__(self, *args, **kwargs):     
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Заголовок'
        self.fields['content'].label = 'Сообщение'

    def save(self):
        new_message = []
        list_phone_numbers = self.cleaned_data.get('user_id')

        title = self.cleaned_data.get('title')
        content = self.cleaned_data.get('content')

        mobile_devices = MobileDevice.objects.filter(status=1, token__isnull=False)
        
        for phone_number in list_phone_numbers:
            mobile_device = mobile_devices.get(phone_number=phone_number)

            new_message.append(
                Message(
                    user_id=mobile_device.user_id,
                    pre_title=content[:255],
                    title=title,
                    content=content
                )
            )

        if new_message:
            Message.objects.bulk_create(new_message)











class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['active', 'internal_description', 'published']

        widgets = {            
            'published': forms.RadioSelect(choices=STATUS, attrs={'class': 'flat'})
        }

class NewsEnForm(forms.ModelForm):
    class Meta:
        model = NewsEn
        fields = ['title', 'content']

class NewsRuForm(forms.ModelForm):
    class Meta:
        model = NewsRu
        fields = ['title', 'content']

class NewsUkForm(forms.ModelForm):
    class Meta:
        model = NewsUk
        fields = ['title', 'content']

class NewsImgForm(forms.ModelForm):
    class Meta:
        model = NewsImg
        fields = ['preview_img_url', 'img_url']
        widgets = {
            'preview_img_url': forms.FileInput(),
            'img_url': forms.FileInput()
        }




class LangImgNewsForm(forms.Form):   
    title = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'col-md-6 col-sm-6 col-xs-12'}))
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'style': 'width:50%'
    }))
    language = forms.CharField(required=False, widget=forms.HiddenInput())    
    img_url = forms.ImageField()
    
    def __init__(self, *args, **kwargs):  
        super().__init__()      
        if ('lang_query' in kwargs and 'img_query' in kwargs and 'language' in kwargs):            
            lang_query = kwargs.pop('lang_query')
            img_query = kwargs.pop('img_query')
            language = kwargs.pop('language')
        else:
            lang_query = None
            img_query = None
            language = None
                
        if (lang_query is not None and img_query is not None):            
            self.fields['title'].initial = lang_query.title           
            self.fields['title'].required = False           
            self.fields['content'].initial = lang_query.content          
            self.fields['content'].required = False
            self.fields['img_url'].required = False         
            self.fields['img_url'].initial = img_query[0].img_url
            self.fields['img_url'].label = '{}'.format('1000*1000')

            for key, value in RESOLUTION.items():
                field_name = 'preview_img_url_{}'.format(key)
                self.fields[field_name] = forms.ImageField(required=False)
                self.fields[field_name].initial = img_query.get(resolution_id=key).preview_img_url
                self.fields[field_name].label = '{}'.format(value)            
        else:
            for key, value in RESOLUTION.items():
                field_name = 'preview_img_url_{}'.format(key)
                self.fields[field_name] = forms.ImageField()
                self.fields[field_name].label = '{}'.format(value)

    # def save(self):
    #     data = self.cleaned_data
    #     print(data)

