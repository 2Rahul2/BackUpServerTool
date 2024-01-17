from django.shortcuts import render ,redirect
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from wsgiref.util import FileWrapper
import zipfile
from pathlib import Path
import mimetypes
import json
import tempfile
import io
import os
import shutil

from .models import *
from django.contrib.auth import authenticate

from django.middleware.csrf import get_token


from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status



from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.http import HttpResponse ,Http404

from django.utils import timezone
import pytz

from .serializers import UserSerializer

def downloadPage(request):
    return render(request ,'app/downloadPage.html')
def download(request):
    filePath = os.path.join(settings.MEDIA_ROOT ,'updata_setup.exe')
    if os.path.exists(filePath):
        with open(filePath ,"rb") as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(filePath)}'
            return response
    raise Http404
@api_view(['POST'])
def signupTest(request):
    try:
        print("here")
        print(request)
        userserializer = UserSerializer(data = request.data)
        print("huhuhhu")
        if userserializer.is_valid():
            if User.objects.filter(username=request.data['username']).exists() or User.objects.filter(email=request.data['email']).exists():
                return Response({"status":"exist"} ,status=status.HTTP_400_BAD_REQUEST)
            userserializer.save()
            user = User.objects.get(username=request.data['username'])
            user.set_password(request.data['password'])
            user.save()
            token = Token.objects.create(user=user)
            return Response({'token':token.key ,'user':userserializer.data ,'status':'created'} , status=status.HTTP_200_OK)
        print("printing after valid statement here")
        return Response({"status":"error" ,"error":userserializer.errors}  ,status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({"status":"error"})

@api_view(['POST'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def loginApi(request):
    try:
        user = get_object_or_404(User ,username = request.data['username'])
        if not user.check_password(request.data['password']):
            return Response({"detail":"Not found."} ,status=status.HTTP_404_NOT_FOUND)
        token , created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        return Response({"detail":"yes","token":token.key ,"user":serializer.data})
    except:
        return Response({"detail":"Not found"} ,status=status.HTTP_404_NOT_FOUND)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    try:
        received_token = request.headers.get('Authorization')
        print("Received Token:", received_token)
        return Response("passed!")
    except:
        return Resposne({"status":"error"})
@api_view(['GET'])
def getToken(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})
@api_view(['POST'])
def javaRequest(request):
    if 'file' in request.FILES:
        file_uploaded = request.FILES['file']
        print(request.FILES)
        print(file_uploaded.read())
        return Response({'message': 'File uploaded successfully'}, status=status.HTTP_201_CREATED)
    else:
        print("got not file lol")
        print(request.FILES)
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
# Create your views here.



def makeDictFiles():
    zip_file_path = 'C:/Users/Rahul/Desktop/File_Sharing/file_sharing/app/filetosent.zip'
    # Create an empty dictionary to represent the structure
    folder_structure = {}
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        print(zip_file.infolist())
        for file_info in zip_file.infolist():
            file_path_parts = file_info.filename.split('/')
            print(file_path_parts)
            current_dict = folder_structure

            # Traverse the dictionary to the correct subfolder level
            for part in file_path_parts[:-1]:
                if part:
                    if part not in current_dict:
                        current_dict[part] = {}
                    current_dict = current_dict[part]
                    # print(current_dict)

                # Add the file to the current subfolder, excluding empty strings
            if file_path_parts[-1]:
                current_dict[file_path_parts[-1]] = None

    # Print the resulting folder structure dictionary

    print(json.dumps(folder_structure, indent=4))

@csrf_exempt
def get_csrf_token(request):
    token = get_token(request)
    print("Token:  " ,token)
    return HttpResponse(str(token))
@api_view(['GET'])
def checkConnection(request):
    if request.method == 'GET':
        # token = get_token(request)
        # print("token :",token)
        return Response(status=status.HTTP_200_OK)
# @csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getZipFiles(request):
    try:
        global totalSize
        def traverseFolder(files ,parentFolder ,parentFolderModelObject , rootId , lst):
            for file in files:
                sizeLst = [0]
                if file.is_dir():
                    subFolderObject = SubFolder.objects.create(name=file.name , mainBranchId = rootId ,SecondaryBranchId = parentFolderModelObject.id)
                    if MainParentName != parentFolder:
                        # print(parentFolder ,"--------" ,file.name)
                        getSubFolderObject = SubFolder.objects.get(id=parentFolderModelObject.id)
                        # getSubFolderObject.subFolder = subFolderObject
                        getSubFolderObject.subFolder.add(subFolderObject)
                        # print(getSubFolderObject.name ,'====' ,subFolderObject.name)
                        getSubFolderObject.save()
                    elif MainParentName == parentFolder:
                        getMainBranchFolderObject = MainBranch.objects.get(id=parentFolderModelObject.id)

                        getMainBranchFolderObject.subFolder.add(subFolderObject)
                        # print(getMainBranchFolderObject.name ,"~~~~~~~~~~" ,subFolderObject.name)
                        getMainBranchFolderObject.save()
                    # parentFolderModelObject.subFolder.add(subFolderObject)
                    # parentFolderModelObject.save()
                    # subFolderObject.save()
                    traverseFolder(file.iterdir() ,file.name ,subFolderObject ,rootId ,sizeLst)
                    folder_size = sizeLst[0]/(1024*1024)
                    subFolderObject.size_mb= folder_size
                    subFolderObject.save()

                    # print(file.name ,"-FOLDER" ,"PARENT:   " ,parentFolder)
                    
                    print(subFolderObject.name  ," Total size  =  " ,sizeLst[0])
                    # for f in file.iterdir():
                    
                else:
                    file_size = 0
                    try:
                        with open(file, 'rb') as f:
                            file_size = f.seek(0, 2)
                            print(f"The size of {f.name} is {file_size} bytes.")
                            sizeLst[0] =  sizeLst[0]+file_size
                            file_size = file_size/(1024*1024)
                           
                            # Use entry.stat().st_size to get the file size
                            # print("SIZE:::  ", file.stat().st_size)
                    except Exception as e:
                        print(f"Error processing file {file.name}: {e}")
                    if parentFolder == MainParentName:
                        MainBranchObject = MainBranch.objects.get(id=parentFolderModelObject.id)
                        fileObject = FolderFiles.objects.create(name=file.name , file=file.read_bytes() ,subBranchId = MainBranchObject.id)
                        
                        fileObject.size_mb = file_size
                        MainBranchObject.files.add(fileObject)
                        fileObject.save()
                        MainBranchObject.save()
                    elif parentFolder != MainParentName:
                        subFolderObject = SubFolder.objects.get(id=parentFolderModelObject.id)
                        fileObject = FolderFiles.objects.create(name=file.name , file=file.read_bytes() ,subBranchId = subFolderObject.id)
                        fileObject.size_mb = file_size
                        subFolderObject.files.add(fileObject)
                        fileObject.save()
                        subFolderObject.save()
                    # print(file.name ,"-FILE")
                lst[0] = lst[0]+sizeLst[0]

        

        if request.method == 'POST':
            # print(get_csrf_token(request))
            # print(request.POST)
            # print(request.FILES['name'])
            # print(request.POST)
            # print(request.FILES)
            # print(request.data)
            zip_file = request.FILES["file"]
            folderName = request.POST['name']


            if zip_file:
                # with open(uploaded_file, 'rb') as zip_file:
                zip_file_data = zip_file.read()
                # print(zip_file_data)
                with tempfile.TemporaryDirectory() as tempDir:
                    new_folder_path = os.path.join(tempDir ,folderName)
                    os.makedirs(new_folder_path)
                    # print("NEW PATH:  " ,new_folder_path)
                    try:
                        with zipfile.ZipFile(io.BytesIO(zip_file_data) ,'r') as zip_file:
                            # zip_file.printdir()
                            zip_file.extractall(new_folder_path)    
                    except Exception as e:
                         print(e)
                    temp_path = Path(tempDir)
                    # print("folder name:  " ,temp_path.name)
                    lst = [0]
                    for f in temp_path.iterdir():
                        totalSize=0
                        if f.is_dir():
                            MainParentName = f.name
                            user = User.objects.get(username=request.data['username'])
                            utc_time = timezone.now()
                            get_time_zone = pytz.timezone("Asia/Calcutta")
                            user_time_zone = utc_time.replace(tzinfo=pytz.utc).astimezone(get_time_zone)
                            format_time = user_time_zone.strftime("%Y-%m-%d %H:%M:%S")
                            mainFolderObject = MainBranch.objects.create(name=f.name ,user=user ,dateInfo=format_time )
                            traverseFolder(f.iterdir() , f.name ,mainFolderObject , mainFolderObject.id ,lst)
                            mainFolderObject.size_mb = ((lst[0])/(1024*1024))
                            mainFolderObject.save()
                            print(mainFolderObject.name  ,"MainFolder Total size  =  " ,lst[0])
                        # lst[0] = lst[0]+anotherLst[0]
                    print(mainFolderObject.name  ,"Final Total size  =  " ,lst[0])   
                return Response({"saved":"okay"} ,status=status.HTTP_200_OK)
            else:
                print("no file uploaded")
                return Response({"saved":"no"} , status=status.HTTP_400_BAD_REQUEST)
        return Response({"saved":"no"})
    except Exception as e:
        print(e)
        return Response({"saved":"no"})


def sendJson(request):
    json_data = {
                    "name":"files" ,
                    "id":256
                }
    return JsonResponse(json_data ,safe=False)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getUserFiles(request):
    try:
        name = request.POST['username']
        user_object = User.objects.filter(username=name)
        if user_object.exists():
            print(request.POST['username'] ,"username over here!")
            dict_object = {}
            getMainBranch = MainBranch.objects.filter(user__username = name).order_by("-dateInfo")

            # why is it not working?
            def addFolderInDict(subFolderObject ,folderName ,dik ,isMain):
                if isMain:
                    formatTime = subFolderObject.dateInfo.strftime("%Y-%m-%d %H:%M:%S")
                    dik[str(subFolderObject.id)+"_"+folderName+"folder"+"_"+str(formatTime)+"$"+str(subFolderObject.size_mb)] = {}
                else:
                    dik[str(subFolderObject.id)+"_"+folderName+"folder"+"$"+str(subFolderObject.size_mb)] = {}
                folderObject = subFolderObject.subFolder.all()
                fileObject = subFolderObject.files.all()
                if folderObject != None:
                    for folder in folderObject:
                        print(folder.name)
                        if isMain:     
                            formatTime = subFolderObject.dateInfo.strftime("%Y-%m-%d %H:%M:%S")                   
                            addFolderInDict(folder ,folder.name ,dik[str(subFolderObject.id)+"_"+folderName+"folder"+"_"+str(formatTime)+"$"+str(subFolderObject.size_mb)] ,False)
                        else:
                            addFolderInDict(folder ,folder.name ,dik[str(subFolderObject.id)+"_"+folderName+"folder"+"$"+str(subFolderObject.size_mb)] ,False)

                if fileObject != None:
                    count = 0
                    for files in fileObject:
                        if isMain:
                            formatTime = subFolderObject.dateInfo.strftime("%Y-%m-%d %H:%M:%S")
                            dik[str(subFolderObject.id)+"_"+folderName+"folder"+"_"+str(formatTime)+"$"+str(subFolderObject.size_mb)]["file"+str(files.id)+"$"+str(files.size_mb)] = files.name
                        else:
                            dik[str(subFolderObject.id)+"_"+folderName+"folder"+"$"+str(subFolderObject.size_mb)]["file"+str(files.id)+"$"+str(files.size_mb)] = files.name

                        count+=1
                        print(folderName  ,"===",files.name)

            index_count = 0
            dict_object = {}
            for folders in getMainBranch:
                # dict_object.update({'type':'folder' ,'name':folders.name})
                addFolderInDict(folders ,folders.name ,dict_object ,True)
                index_count += 1
                # subFolderObject = folders.subFolder.all()
                # for subFolder in subFolderObject:
                    # print(subFolder.name)
            # print(getMainBranch)

            print(json.dumps(dict_object ,indent=4))
            print(len(dict_object))
            return JsonResponse(dict_object ,safe=False)
        else:
            return Response("Error")    
    except Exception as error:
        print(error)
        return Response("Error")



def home(request):
    zipPath = "C:/Users/Rahul/Desktop/File_Sharing/file_sharing/app/filetosent.zip"
    def zip_extract_function(zip_file , folder_path):
        print("FOLDER" ,folder_path)
        files_in_folder = []    

        for file_info in zip_file.infolist():
            if file_info.filename.startswith(folder_path) and not file_info.filename.endswith('/'):
                # fileInfo.filename is a file within the specified folder
                files_in_folder.append(file_info.filename)

        # Print or process the files in the current folder
        for file_name in files_in_folder:
            print(f"File in folder {folder_path}: {file_name}")

        subfolder_paths = []
        for file_info in zip_file.infolist():
            if file_info.filename.startswith(folder_path) and file_info.filename.endswith('/'):
                subfolder_paths.append(file_info.filename)

        for subfolder_path in subfolder_paths:
            zip_extract_function(zip_file, subfolder_path)

    pathName = 'C:/Users/Rahul/Desktop/File_Sharing/file_sharing/app/filetosent'
    dirt = Path(pathName)
    files = list(dirt.iterdir())
    for f in files:
        pass
    # MainParentName = pathName.split('/')[-1]
    
    def traverseFolder(files ,parentFolder ,parentFolderModelObject):
        for file in files:
            if file.is_dir():
                subFolderObject = SubFolder.objects.create(name=file.name ,mainBranchId = parentFolderModelObject.id)
                if MainParentName != parentFolder:
                    print(parentFolder ,"--------" ,file.name)
                    getSubFolderObject = SubFolder.objects.get(name=parentFolder)
                    # getSubFolderObject.subFolder = subFolderObject
                    getSubFolderObject.subFolder.add(subFolderObject)
                    print(getSubFolderObject.name ,'====' ,subFolderObject.name)
                    getSubFolderObject.save()
                elif MainParentName == parentFolder:
                    getMainBranchFolderObject = MainBranch.objects.get(name=parentFolder)
                    getMainBranchFolderObject.subFolder.add(subFolderObject)
                    print(getMainBranchFolderObject.name ,"~~~~~~~~~~" ,subFolderObject.name)
                    getMainBranchFolderObject.save()
                # parentFolderModelObject.subFolder.add(subFolderObject)
                # parentFolderModelObject.save()
                subFolderObject.save()
                print(file.name ,"-FOLDER" ,"PARENT:   " ,parentFolder)
                traverseFolder(file.iterdir() ,file.name ,subFolderObject)
                # for f in file.iterdir():
                  
            else:
                if parentFolder == MainParentName:
                    MainBranchObject = MainBranch.objects.get(name=parentFolder)
                    fileObject = FolderFiles.objects.create(name=file.name , file=file.read_bytes() ,subBranchId = MainBranchObject.id)
                    MainBranchObject.files.add(fileObject)
                    fileObject.save()
                    MainBranchObject.save()
                elif parentFolder != MainParentName:
                    subFolderObject = SubFolder.objects.get(name=parentFolder)
                    fileObject = FolderFiles.objects.create(name=file.name , file=file.read_bytes() ,subBranchId = subFolderObject.id)
                    subFolderObject.files.add(fileObject)
                    fileObject.save()
                    subFolderObject.save()
                print(file.name ,"-FILE")
    
    with open(zipPath, 'rb') as zip_file:
        zip_file_data = zip_file.read()
    with tempfile.TemporaryDirectory() as tempDir:
        with zipfile.ZipFile(io.BytesIO(zip_file_data) ,'r') as zip_file:
            zip_file.extractall(tempDir)
        temp_path = Path(tempDir)
        for f in temp_path.iterdir():
            if f.is_dir():
                print(f.iterdir())
                MainParentName = f.name
                # mainFolderObject = MainBranch.objects.create(name=pathName.split('/')[-1])
                mainFolderObject = MainBranch.objects.create(name=f.name)
                mainFolderObject.save()
                traverseFolder(f.iterdir() , f.name ,mainFolderObject)
        
        # traverseFolder(zip_file , '')
        # fileData = Path(zip_file.infolist())

    def create_folder_structure(folderModel ,parent_folder_path):
        current_folder_path = os.path.join(parent_folder_path , folderModel.name)
        os.makedirs(current_folder_path)
        try:
            for fileModel in folderModel.files.all():
                filePath = os.path.join(current_folder_path ,fileModel.name)
                print(fileModel.name)
                with open(filePath ,'wb') as f:
                    f.write(fileModel.file)
        except:
            pass
        for SubfolderModel in folderModel.subFolder.all():
            create_folder_structure(SubfolderModel , current_folder_path)

    def populate_folder_dir(temp_dir_path):
        root_folder_path = os.path.join(temp_dir_path ,'filetosentNew')
        os.makedirs(root_folder_path)

        for folderModel in MainBranch.objects.filter(id=40):
            create_folder_structure(folderModel , root_folder_path)
    def GetFiles():
        get_temp_dir = tempfile.TemporaryDirectory()
        populate_folder_dir(get_temp_dir.name)


        
        # zipFileName = get_temp_dir.name+'.zip'
        # shutil.make_archive(get_temp_dir.name , 'zip' ,get_temp_dir.name)
        # shutil.move(zipFileName ,'C:/Users/Rahul/Desktop/File_Sharing/file_sharing')
        # savePathDirectory = 'C:\Users\Rahul\Desktop\File_Sharing\file_sharing'

    # GetFiles()


    return render(request ,'app/index.html')


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getData(request):
    try:
            
        def create_folder_structure(folderModel ,parent_folder_path):
            current_folder_path = os.path.join(parent_folder_path , folderModel.name)
            os.makedirs(current_folder_path)
            try:
                for fileModel in folderModel.files.all():
                    filePath = os.path.join(current_folder_path ,fileModel.name)
                    # print(fileModel.name)
                    with open(filePath ,'wb') as f:
                        f.write(fileModel.file)
            except:
                pass
            for SubfolderModel in folderModel.subFolder.all():
                create_folder_structure(SubfolderModel , current_folder_path)
            # print(current_folder_path)

        def populate_folder_dir(temp_dir_path ,branchType ,fileType ,id):
            # root_folder_path = os.path.join(temp_dir_path ,'filetosentNew')
            # os.makedirs(root_folder_path)
            # os.makedirs(temp_dir_path)
            if branchType == "mainBranch":
                for folderModel in MainBranch.objects.filter(id=id):
                    create_folder_structure(folderModel , temp_dir_path)
            elif branchType == "subBranch":
                for folderModel in SubFolder.objects.filter(id=id):
                    create_folder_structure(folderModel ,temp_dir_path)
            elif branchType == "file":
                file = FolderFiles.objects.get(id=id)
                filePath = os.path.join(temp_dir_path ,file.name)
                os.makedirs(filePath)
                fileWritePath = os.path.join(filePath ,file.name)
                with open(fileWritePath ,"wb") as f:
                    f.write(file.file)
        def file_iter(dir_path):
            print("dir_path:", dir_path)
            for root ,_ ,files in  os.walk(dir_path):
                print("Entering os.walk loop")
                print("Files in this directory:", files)
                for fileName in files:
                    file_path = os.path.join(root , fileName)
                    print("Processing file:", file_path)
                    with open(file_path , 'rb') as file:
                        yield FileWrapper(file)

        # if request.method == "GET":
        #     pass
        if request.method == "POST":
            username = request.POST['username']
            # password = request.POST['password']

            if User.objects.filter(username=username).exists():
                branchType = request.POST["branchType"]
                fileType = request.POST["file"]
                id = int(request.POST["id"])
                get_temp_dir = tempfile.TemporaryDirectory()
                populate_folder_dir(get_temp_dir.name ,branchType ,fileType ,id)
                # response = HttpResponse(FileWrapper(open(get_temp_dir.name)) ,content_type = 'application/octet-stream')
                # print("heree??")

                zip_filename = get_temp_dir.name + '.zip'
                shutil.make_archive(get_temp_dir.name, 'zip', get_temp_dir.name)

                # Open and read the saved zip file
                with open(zip_filename, 'rb') as zip_file:
                    response = HttpResponse(zip_file.read(), content_type='application/zip')
                # response = StreamingHttpResponse(file_iter(os.path.join(get_temp_dir.name ,'filetosentNew')) ,content_type = 'application/octet-stream')
                # print("or here?")
                response['Content-Disposition'] = f'attachment; filename="your_folder_name.zip"'
                # def GetFiles():
                response['Status'] = "Yes"
                get_temp_dir.cleanup()
                os.remove(zip_filename)            
                return response
            
            response = HttpResponse()
            response['Status'] = "No"
            return response
        
    except:
        pass
    
@csrf_exempt
def javaSignIn(request):
    if request.method == "POST":
        name = request.POST['name']
        password = request.POST['password']
        # return HttpResponse("okay")
        try:
            userModel = authenticate(username=name ,password=password)
            print("User mode:  ",userModel)
            if userModel is not None:
                print("ysss")
                return HttpResponse("okay")
            else:
                print("hehe")
                return HttpResponse("not okay")
        except:
            print("hhgehehhehehe")
            return HttpResponse("error")
        return HttpResponse(status.HTTP_406_NOT_ACCEPTABLE)

def loginAccount(request):
    return render(request ,'app/login.html')

def createAccount(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        username = data["username"]
        password = data["password"]

        userModel = User.objects.filter(username = username)
        # userModel.set_password(password)
        userNameCheck = User.objects.filter(username=username)
        if (userNameCheck) != None:
            if len(userModel) != 0:
                print(userModel)
                return JsonResponse(json.dumps({"status":"Account exists"}),safe=False)
            else:
                NewUser = User.objects.create_user(username=username ,password=password)
            
                return JsonResponse(json.dumps({"status":"Account created"}) ,safe=False)
        else:
            print(userNameCheck[0].get_username)
            return JsonResponse(json.dumps({"status":"User Already exists"}) ,safe=False)
def createAccountPage(request):

    return render(request ,'app/account.html')

def create(request):
    if request.method == "POST":
        email = "email"
        userObject = User.objects.get(email=email)
        data = json.loads(request.body.decode('utf-8'))

            # Now you can access the JSON data as a Python dictionary
        print(data)
        return JsonResponse({"status":"hehe"})
    
# def home(request):
#     directory = ""
#     zipPath = "C:/Users/Rahul/Desktop/File_Sharing/file_sharing/app/filetosent.zip"
#     with zipfile.ZipFile(zipPath ,'r') as zip_file:
#         print(zip_file.infolist())
#         for fileInfo in zip_file.infolist():
#             directory = fileInfo.filename
#             if fileInfo.filename.endswith('/'):
#                 print(fileInfo.filename)
#                 pass
#             else:
#                 # print(directory)
#                 # print(fileInfo.filename)
#                 with zip_file.open(fileInfo.filename) as file:
#                     line = file.readlines()
#                     # print(line)
#                 # with open(fileInfo.filename.split('/')[-1]) as f:
#                 #     line = f.readlines()
#                 #     print(line)
#                 # print('file:' ,fileInfo.filename.split('/')[-1])
#     return render(request ,'app/index.html')

def saveFiles(request):
    for folderModel in MainBranch.objects.filter(id=200):
        print(folderModel.name)
    return HttpResponse("heh")
