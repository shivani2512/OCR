import mimetypes
from wsgiref.util import FileWrapper
from django.http import FileResponse
from django.utils.text import slugify
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.encoding import smart_str
import django.core.files
from .forms import UserForm, UploadForm, LoginForm
from .models import User, Upload
from django.views.generic import (TemplateView, ListView,
                                  DetailView, UpdateView)
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from .backends import EmailBackend
from django.core.mail import send_mail
from django.conf import settings
from datetime import date
import os
import shutil
import glob
import time
import fnmatch
from pathlib import Path
from pdf2image import convert_from_bytes
import cv2
import re
from matplotlib.pyplot import imsave
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import os
from django.conf import settings
from django.http import HttpResponse, Http404



def login_user(request):

    email = request.POST.get('email')
    password = request.POST.get('password')
    # form = UserForm(request.POST)
    remember_me = request.POST.get('remember_me', False)

    user = EmailBackend.authenticate(username=email, password=password)
    if user:
        # print(user.email, user.password)
        if user.is_is_active:
            login(request, user, backend='ocr_app.backends.EmailBackend')
            if not remember_me:
                request.session.set_expiry(0)
            return HttpResponseRedirect(reverse('index'))
        else:
            print("Not active")
    else:
        print("wrong person tried to access.")
    return render(request, 'registration/login.html', {})



@login_required()
def logout_user(request):
    for r, d, f in os.walk("media/upload"):
        for file in f:
            os.remove(os.path.join(r, file))

    logout(request)
    return redirect('index')


# def login(request):
#     email = request.POST.get('email')
#     password = request.POST.get('password')
#     remember_me = request.POST.get('remember_me', False)
#     user_form = LoginForm(data=request.POST)
#     user = EmailBackend.authenticate(username=email, password=password)
#     if user.is_is_active:
#         login(request, user)
#         if not remember_me:
#             request.session.set_expiry(0)
#             return HttpResponseRedirect(reverse('index'))
#         else:
#             print("Not active")
#     else:
#         print("wrong person tried to access.")
#     return render(request, 'registration/login.html', {})
#

def registration(request):
    register = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            register = True
        else:
            print(user_form.errors)
    else:
        user_form = UserForm()

    return render(request, 'registration/register.html', {'user_form': user_form,
                                             'register': register})


class Index(TemplateView):
    model = User
    template_name = 'index.html'


class Home(TemplateView):
    model = User
    template_name = 'home.html'


def UploadImage(request,pk=None):
    upload = False
    user = User.objects.get(pk=pk)
    # print()

    if request.method == 'POST':
        uploadForm = UploadForm(request.POST, request.FILES)

        if uploadForm.is_valid():
            user.save()
            upload = uploadForm.save(commit=False)
            upload.user = request.user
            upload.save()

            upload = True
        else:
            print(uploadForm.errors)
    else:
        uploadForm = UploadForm()
    return render(request, 'upload.html', {'upload_form': uploadForm,
                                           'upload': upload})


pdf_dir = "media/upload"


def extract_image():
    tiff_image = []
    for r, d, f in os.walk(pdf_dir):
        for file in f:
            if '.tiff' in file:
                tiff_image.append(os.path.join(r, file))


    # Original Image
    pdf_files = glob.glob("%s/*.pdf" % pdf_dir)
    for file in pdf_files:
        # print(file)
        file_base = os.path.basename(file)
        # print(file_base)

        images = convert_from_bytes(open(file, 'rb').read())
        image_counter = 1
        for page in images:
            # print("inside")
            filename_pdf = pdf_dir + "/" + os.path.splitext(file_base)[0] + "_" + str(image_counter) + ".pdf"
            print(filename_pdf)
            pdf = pytesseract.image_to_pdf_or_hocr(page, extension='pdf', lang='eng')
            print(filename_pdf + "is created")
            page.save(filename_pdf, 'pdf')
            image_counter = image_counter + 1
            # t = open(filename_pdf, "w+b")


    for tiff in tiff_image:
        parent = Path(tiff).parent
        # print(parent)
        path = os.path.basename(parent)
        # print(path)
        tiff_base = os.path.basename(tiff)
        # print(tiff_base)
        # Below this:
        # filename_pdf = pdf_dir + "/" + os.path.splitext(tiff_base)[0] + ".pdf"

        # print(filename_pdf)
        filename_text = pdf_dir + "/" + os.path.splitext(tiff_base)[0] + ".txt"
        # print(filename_text)
        # filename_text.save(filename_text)

        # Below this:
        # pdf = pytesseract.image_to_pdf_or_hocr(tiff, extension='pdf', lang='eng')
        txt = pytesseract.image_to_string(tiff, lang='eng')
        t = open(filename_text, "w+b")
        # Below this:
        # f = open(filename_pdf, "w+b")
        # if f:
        #     f.write(bytearray(pdf))
        #     f.close()
        #     print(filename_pdf + "is created")
        # else:
        #     print(filename_pdf + "not created")
        if t:
            t.write(txt.encode())
            t.close()
            print(filename_text + "is created")
        else:
            print(filename_text + "is not created")

        os.remove(tiff)
def select_option(option):

    jpg_image = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(pdf_dir):
        for file in f:
            if '.jpg' in file:
                jpg_image.append(os.path.join(r, file))


    if int(option) == 1:
        # print("inside op 1")
        for jpg in jpg_image:
            parent = Path(jpg).parent
            path = os.path.basename(parent)
            # print(path)
            jpg_base = os.path.basename(jpg)
            d = path + "/" + jpg_base
            # print(d)
            image1 = cv2.imread(jpg)
            gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
            filename = os.path.splitext(jpg)[0] + ".tiff"
            print(filename)
            ret, thresh1 = cv2.threshold(gray, 120, 255, cv2.THRESH_TOZERO)
            imsave(filename, thresh1, format='tiff', dpi=300)
            os.remove(jpg)

    elif int(option) == 2:
        for jpg in jpg_image:
            parent = Path(jpg).parent
            path = os.path.basename(parent)
            jpg_base = os.path.basename(jpg)
            d = path + "/" + jpg_base
            image1 = cv2.imread(jpg)
            gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
            filename = os.path.splitext(jpg)[0] + ".tiff"
            print(filename)
            thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 199, 5)
            imsave(filename, thresh2, format='tiff', dpi=300)
            os.remove(jpg)

    elif int(option) == 3:
        for jpg in jpg_image:
            parent = Path(jpg).parent
            path = os.path.basename(parent)
            jpg_base = os.path.basename(jpg)
            d = path + "/" + jpg_base
            image1 = cv2.imread(jpg)
            gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
            filename = os.path.splitext(jpg)[0] + ".tiff"
            print(filename)
            thresh3 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 199, 5)
            imsave(filename, thresh3, format='tiff', dpi=300)
            os.remove(jpg)

    elif int(option) == 4:
        print("inside op 4:")
        for jpg in jpg_image:
            parent = Path(jpg).parent
            path = os.path.basename(parent)
            # print(path)
            jpg_base = os.path.basename(jpg)
            d = path + "/" + jpg_base
            image1 = cv2.imread(jpg)
            gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
            filename = os.path.splitext(jpg)[0] + ".tiff"
            print(filename)
            ret, thresh4 = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            imsave(filename, thresh4, format='tiff', dpi=300)
            os.remove(jpg)


def convert_into_jpeg(pdf):
    pdf_files = glob.glob("%s/*.pdf" % pdf_dir)
    for file in pdf_files:
        # print(file)
        file_base = os.path.basename(file)
        print(file_base)

        images = convert_from_bytes(open(file, 'rb').read())
        image_counter = 1
        for page in images:
            filename = pdf_dir + "/" + os.path.splitext(file_base)[0] + "_" + str(image_counter) + ".jpg"
            print(filename)
            page.save(filename, 'JPEG')
            image_counter = image_counter + 1

# def convert_into_jpg(input_path, process_path, output_path, option):
#     print(input_path)
#     print(process_path)
#     print(output_path)
#     global date_dir
#
#
#     date_dir = str(process_path + "/" + today)
#     pdf_files = glob.glob("%s/*.pdf" % input_path)
#
#     #Creatind date_dir
#     if os.path.exists(date_dir):
#         print(date_dir + "exsits")
#     else:
#         print(os.makedirs(date_dir), " is created")
#         # print(d + " is Created")
#     #
#     def perform(d):
#         # print(type(d))
#         dr_files = glob.glob("%s/*.pdf" % d)
#         for file in dr_files:
#             file_base = os.path.basename(file)
#             images = convert_from_bytes(open(file, 'rb').read())
#             image_counter = 1
#             for page in images:
#                 filename = d + "/" + os.path.splitext(file_base)[0] + "_" + str(image_counter) + ".jpg"
#                 print(filename)
#                 page.save(filename, 'JPEG')
#                 image_counter = image_counter + 1
#
#     def check(file):
#         path = os.path.basename(file)
#         print(file)
#         if os.path.isfile(file):
#             global name
#             name = file
#         cnt = 1
#         if os.path.isdir(date_dir + "/" + os.path.splitext(path)[0]):
#             # cnt = max([re.findall("_").join(find_name.split("_")[0:-1]+"_"+"(.*?)$",find_name for find_name in os.listdir(os.path.join(converted_image_path,d))]))
#             d = date_dir + "/" + os.path.splitext(path)[0] + "_" + str(cnt)
#             cnt += 1
#             check(d)
#         else:
#             d = date_dir + "/" + os.path.splitext(path)[0]
#             os.makedirs(d)
#             print(d + "is created")
#             shutil.copy(name, d)
#             perform(d)
#     #
#     for file in pdf_files:
#         check(file)


# def select_option(option, process_path):
#
#     date_dir = str(process_path + "/" + today)
#     print(date_dir)
#     # print(date_dir)
#     jpg_image = []
#     # r=root, d=directories, f = files
#     for r, d, f in os.walk(date_dir):
#         for file in f:
#             if '.jpg' in file:
#                 jpg_image.append(os.path.join(r, file))
#
#     if int(option) == 1:
#         # print("inside op 1")
#         for jpg in jpg_image:
#             parent = Path(jpg).parent
#             path = os.path.basename(parent)
#             # print(path)
#             jpg_base = os.path.basename(jpg)
#             d = path + "/" + jpg_base
#             # print(d)
#             image1 = cv2.imread(jpg)
#             gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
#             filename = os.path.splitext(jpg)[0] + ".tiff"
#             print(filename)
#             ret, thresh1 = cv2.threshold(gray, 120, 255, cv2.THRESH_TOZERO)
#             imsave(filename, thresh1, format='tiff', dpi=300)
#             os.remove(jpg)
#
#     elif int(option) == 2:
#         for jpg in jpg_image:
#             parent = Path(jpg).parent
#             path = os.path.basename(parent)
#             jpg_base = os.path.basename(jpg)
#             d = path + "/" + jpg_base
#             image1 = cv2.imread(jpg)
#             gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
#             filename = os.path.splitext(jpg)[0] + ".tiff"
#             print(filename)
#             thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 199, 5)
#             imsave(filename, thresh2, format='tiff', dpi=300)
#             os.remove(jpg)
#
#     elif int(option) == 3:
#         for jpg in jpg_image:
#             parent = Path(jpg).parent
#             path = os.path.basename(parent)
#             jpg_base = os.path.basename(jpg)
#             d = path + "/" + jpg_base
#             image1 = cv2.imread(jpg)
#             gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
#             filename = os.path.splitext(jpg)[0] + ".tiff"
#             print(filename)
#             thresh3 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 199, 5)
#             imsave(filename, thresh3, format='tiff', dpi=300)
#             os.remove(jpg)
#
#     elif int(option) == 4:
#         print("inside op 4:")
#         for jpg in jpg_image:
#             parent = Path(jpg).parent
#             path = os.path.basename(parent)
#             # print(path)
#             jpg_base = os.path.basename(jpg)
#             d = path + "/" + jpg_base
#             image1 = cv2.imread(jpg)
#             gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
#             filename = os.path.splitext(jpg)[0] + ".tiff"
#             print(filename)
#             ret, thresh4 = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#             imsave(filename, thresh4, format='tiff', dpi=300)
#             os.remove(jpg)
#

# def extract_image(output_path, process_path, input_path):
#
#     # print(outputpath)
#     date_dir = str(process_path + "/" + today)
#
#
#     tiff_image = []
#     for r, d, f in os.walk(date_dir):
#         for file in f:
#             if '.tiff' in file:
#                 tiff_image.append(os.path.join(r, file))
#     pdf_files = glob.glob("%s/*.pdf" % input_path)
#     extract_date_dir = str(output_path + "/" + today)
#
#     # for tif in tiff_image:
#     #     print(tif)
#
#     def convert_image():
#         # def convert():
#         for tiff in tiff_image:
#             parent = Path(tiff).parent
#             path = os.path.basename(parent)
#             tiff_base = os.path.basename(tiff)
#
#             filename_pdf = extract_date_dir + "/" + path + "/" + os.path.splitext(tiff_base)[0] + ".pdf"
#             print(filename_pdf)
#             filename_text = extract_date_dir + "/" + path + "/" + os.path.splitext(tiff_base)[0] + ".txt"
#             print(filename_text)
#             pdf = pytesseract.image_to_pdf_or_hocr(tiff, extension='pdf', lang='eng')
#             txt = pytesseract.image_to_string(tiff, lang='eng')
#             t = open(filename_text, "w+b")
#             f = open(filename_pdf, "w+b")
#             if f:
#                 f.write(bytearray(pdf))
#                 f.close()
#             else:
#                 print(filename_pdf + "not created")
#             if t:
#                 t.write(txt.encode())
#                 t.close()
#             else:
#                 print(filename_text + "is not created")
#
#     def check(file):
#         path = os.path.basename(file)
#         if os.path.isfile(file):
#             global name
#             name = file
#         # print(path)
#         # Make changes here
#         cnt = 1
#         if os.path.isdir(extract_date_dir + "/" + os.path.splitext(path)[0]):
#             d = extract_date_dir + "/" + os.path.splitext(path)[0] + "_" + str(cnt)
#             cnt += 1
#             check(d)
#         else:
#             # oldName = os.path.splitext(path)[0] + ".pdf"
#             d = extract_date_dir + "/" + os.path.splitext(path)[0]
#             os.makedirs(d)
#             shutil.copy(name, d)
#             print(d + "is created")
#             convert_image()
#
#             # perform(d)
#
#     for file in pdf_files:
#         check(file)


def download_item(request, file_name):
    print(file_name)
    '''
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    print(file_path)
    if os.path.exists("/home/shivani/PycharmProjects/OCR/OCR/media/upload/TestLink.pdf"):
        print("path")
        with open("/home/shivani/PycharmProjects/OCR/OCR/media/upload/TestLink.pdf", 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
            return response
    else:
        print("Error")
    '''

def ImageProcess(request, pk=None):

    uploadObj = Upload.objects.all().filter(user=pk)
    print(pk)
    global pdf, option
    for value in uploadObj:
        pdf = value.File
        option = value.operation
        # print(pdf)
    convert_into_jpeg(pdf)
    select_option(option)
    extract_image()
    # Download
    # value = []
    # for r, d, f in os.walk("media/upload"):
    #     for file in f:
    #         value.append(os.path.join(r, file))
    #
    # for val in value:
    #     if os.path.exists(val):
    #         with open(val, 'rb') as fh:
    #             response = HttpResponse(fh.read(), content_type="application/pdf")
    #             response['Content-Disposition'] = 'inline; filename=' + os.path.basename(val)
    #         # return render(request, "complete.html", {'value': response})
    #         return response
    #     else:
    #         print("Error")



        # download_item(request, val)
        # print(val)

    # return render(request, "complete.html", {'value': value})

    # download_item()
    # item = "/home/shivani/PycharmProjects/OCR/OCR/media/upload/TestLink.pdf"
    # value = []
    # path = "upload/"
    # for r, d, f in os.walk("media/upload"):
    #     for file in f:
    #         value.append(os.path.join(r, file))
    #
    # file_path = os.path.join(settings.MEDIA_ROOT, path)
    # if os.path.exists(file_path):
    #     for f in value:
    #         with open(f, 'rb') as fh:
    #             response = HttpResponse(fh.read(), content_type="application/pdf")
    #             response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
    #             return render(request, "complete.html", {'value': response})
    #     raise Http404
    # value = []
    # for r, d, f in os.walk("media/upload"):
    #     for file in f:
    #         value.append(os.path.join(r, file))
    #
    # for i in value:
    #     print(os.path.basename(i))
    #     path = "upload"
    #     file_path = os.path.join(settings.MEDIA_ROOT, path)
    #     if os.path.exists(file_path):
    #         with open(i, 'rb') as fh:
    #             response = HttpResponse(fh.read(), content_type="application/pdf")
    #             response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
    #         return render(request, "complete.html", {'res': response, 'value': value})
    #     raise Http404
    # return render(request, "complete.html", {})


    # fileObj = FileConfig.objects.all().filter(user=pk)
    # global input_path, process_path, output_path, option
    # for value in fileObj:
    #     input_path = value.inputFolder
    #     process_path = value.processFolder
    #     output_path = value.outputFolder
    #     option = value.operation

    # print(input_path)
    # print(process_path)
    # print(output_path)
    # print(option)

    # convert_into_jpg(input_path, process_path, output_path, option)
    # select_option(option, process_path)
    # extract_image(output_path, process_path, input_path)

    # return render_to_response('files_list.html',{'total_files':os.listdir(settings.MEDIA_ROOT),'path':settings.MEDIA_ROOT}, context_instance=RequestContext(request))
    #

    # Working properly...
    value = []
    for r, d, f in os.walk("media/upload"):
        for file in f:
            value.append(os.path.join(r, file))

    for val in value:
        print(val)

    return render(request, "complete.html", {'value': value})



#
# def download(request, file_path):
#     """
#     e.g.: file_path = '/tmp/file.pdf'
#     """
#     try:
#         wrapper = FileWrapper(open(file_path, 'rb'))
#         response = HttpResponse(wrapper, content_type='application/force-download')
#         response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
#         return response
#     except Exception as e:
#         return None
#     return response

def FileConfigurationForm(request, pk=None):
    user = User.objects.get(pk=pk)
    # print(request.user)
    register = False

    if request.method == 'POST':
        Config_form = FileConfigForm(request.POST, request.FILES)

        if Config_form.is_valid():
            user.save()

            profile = Config_form.save(commit=False)
            profile.user = request.user
            profile.save()

            register = True
        else:
            print(Config_form.errors)
    else:
        Config_form = FileConfigForm()

    return render(request, 'FileConfig.html', {'form': Config_form,
                                             'register': register})
