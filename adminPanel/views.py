from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, response, QueryDict
import json
import smtplib
from email.mime.text import MIMEText
# from os.path import basename
# from email.mime.application import MIMEApplication
# from email.mime.multipart import MIMEMultipart
import smtplib
from django.http.response import HttpResponseServerError
import firebase_admin
from firebase_admin import credentials,firestore
import razorpay
import hashlib
import uuid
import boto3
from boto3.dynamodb.conditions import Attr, Key
from decimal import Decimal

# DynamoDB Cursor
db = boto3.resource(service_name = 'dynamodb',region_name = 'us-east-1',
        aws_access_key_id = 'AKIAWUIFHJLFHNQCPCPY',
        aws_secret_access_key = 'boUoP1NaUl4KnfWB8kjAs4UJtScVpd8CxgokahL5')

# Constants
UNI_DOC_ID = '89f955f222844bb79b60afc27fc99314'

# Create your views here.
def adminLogin(request):
    if (request.session.get('adminLogin') == None):
        return render(request, 'adminLogin.html')
    else:
        return redirect("/adminPanel/adminDashboard/", {'adminName':request.session['adminLogin'], 'currentPage':'adminDashboard', 'sidebarHeading':'adminDashboard'})
# Admin Login Logic
def loginAdmin(request):
    receivedData = json.loads(str(request.body, encoding='utf-8'))
    adminData = db.Table('ADMIN').get_item(Key = {'email':receivedData['email']})
    if 'Item' in adminData.keys():
        adminData = adminData['Item']
        if (hashlib.md5(receivedData['password'].encode()).hexdigest() == adminData['password']):
            del adminData['password']
            request.session['adminLogin'] = adminData['name'].split()[0]
            request.session.modified = True
            return JsonResponse({'status':'success', 'adminName':adminData['name'].split()[0]})
        else:
            return JsonResponse({'status':'wrongPass'})
    else:
        return JsonResponse({'status':'notFound'})

# Admin logout logic
def logoutAdmin(request):
    del request.session['adminLogin']
    request.session.modified = True
    return JsonResponse({'status':'success'})

# Admin Dashboard
def adminDashboard(request):
    if (request.method == 'POST'):
        receivedData = QueryDict(request.body).dict()
        cardData = db.Table('UNIVERSAL').get_item(Key={'docId':UNI_DOC_ID})['Item']
        return render(request, 'adminDashboard.html', {'adminName':receivedData['name'], 'cardData':cardData,
        'currentPage':'adminDashboard', 'sidebarHeading':'adminDashboard'})
    elif (request.session.get('adminLogin') == None):
        return redirect('/adminPanel/')
    else:
        cardData = db.Table('UNIVERSAL').get_item(Key={'docId':UNI_DOC_ID})['Item']
        return render(request, 'adminDashboard.html', {'adminName':request.session['adminLogin'], 'cardData':cardData,
        'currentPage':'adminDashboard', 'sidebarHeading':'adminDashboard'})
# Get data to make the dashboard graph
def adminDashboardGraph(request):
    receivedData = json.loads(str(request.body, encoding='utf-8'))
    ordersList = []
    print(receivedData)
    if receivedData['filterBy'] == 'ordersPlaced':
        dataQuery = db.Table('ORDERS').scan(
            Select='ALL_ATTRIBUTES',
            FilterExpression=Attr('orderStatus').eq('pending')
                            & (Attr('orderTimestamp').gt(receivedData['startTimestamp']) | Attr('orderTimestamp').eq(receivedData['startTimestamp'])) 
                            & (Attr('orderTimestamp').lt(receivedData['endTimestamp']) | Attr('orderTimestamp').eq(receivedData['endTimestamp']))
        )
        ordersList = dataQuery['Items']
        while 'LastEvaluatedKey' in dataQuery:
            dataQuery = db.Table('ORDERS').scan(
                ExclusiveStartKey=productQuery['LastEvaluatedKey'],
                Select='ALL_ATTRIBUTES',
                FilterExpression=Attr('orderStatus').eq('pending')
                                & (Attr('orderTimestamp').lt(receivedData['endTimestamp']) | Attr('orderTimestamp').eq(receivedData['endTimestamp']))
                                & (Attr('orderTimestamp').gt(receivedData['startTimestamp']) | Attr('orderTimestamp').eq(receivedData['startTimestamp']))
            )
            ordersList.extend(productQuery['Items'])
    else:
        dataQuery = db.Table('ORDERS').scan(
            Select='ALL_ATTRIBUTES',
            FilterExpression=Attr('orderStatus').eq('completed')
                            & (Attr('orderTimestamp').gt(receivedData['startTimestamp']) | Attr('orderTimestamp').eq(receivedData['startTimestamp'])) 
                            & (Attr('orderTimestamp').lt(receivedData['endTimestamp']) | Attr('orderTimestamp').eq(receivedData['endTimestamp']))
        )
        ordersList = dataQuery['Items']
        while 'LastEvaluatedKey' in dataQuery:
            dataQuery = db.Table('ORDERS').scan(
                ExclusiveStartKey=productQuery['LastEvaluatedKey'],
                Select='ALL_ATTRIBUTES',
                FilterExpression=Attr('orderStatus').eq('completed')
                                & (Attr('orderTimestamp').lt(receivedData['endTimestamp']) | Attr('orderTimestamp').eq(receivedData['endTimestamp']))
                                & (Attr('orderTimestamp').gt(receivedData['startTimestamp']) | Attr('orderTimestamp').eq(receivedData['startTimestamp']))
            )
            ordersList.extend(productQuery['Items'])
    # Sort the list by timestamp
    ordersList = sorted(ordersList, key=lambda d: d['orderTimestamp'])
    return JsonResponse({'status':'success', 'ordersList':ordersList})

# Add new product
def addProduct(request):
    if (request.method == 'POST'):
        receivedData = QueryDict(request.body).dict()
        return render(request, 'addProduct.html', {'adminName':receivedData['name'], 'currentPage':'addProduct', 'sidebarHeading':'products'})
    elif (request.session.get('adminLogin') == None):
        return redirect('/adminPanel/')
    else:
        return render(request, 'addProduct.html', {'adminName':request.session['adminLogin'], 'currentPage':'addProduct', 'sidebarHeading':'products'})
# Save Product Data sent from addProduct page
def saveNewProduct(request):
    receivedData = json.loads(str(request.body, encoding='utf-8'))
    receivedData['docId'] = uuid.uuid4().hex
    db.Table('PRODUCTS').put_item(Item=receivedData)
    return JsonResponse({'status':'success'})

# Updae product page
def editProduct(request):
    if (request.method == 'POST'):
        receivedData = QueryDict(request.body).dict()
        productQuery = db.Table('PRODUCTS').scan()
        productList = productQuery['Items']
        while 'LastEvaluatedKey' in productQuery:
            productQuery = db.Table('PRODUCTS').scan(
                ExclusiveStartKey=productQuery['LastEvaluatedKey']
            )
            productList.extend(productQuery['Items'])
        return render(request, 'editProduct.html', {'productList':productList, 'adminName':receivedData['name'], 'currentPage':'editProduct', 'sidebarHeading':'products'})
    elif (request.session.get('adminLogin') == None):
        return redirect('/adminPanel/')
    else:
        productQuery = db.Table('PRODUCTS').scan()
        productList = productQuery['Items']
        while 'LastEvaluatedKey' in productQuery:
            productQuery = db.Table('PRODUCTS').scan(
                ExclusiveStartKey=productQuery['LastEvaluatedKey']
            )
            productList.extend(productQuery['Items'])
        return render(request, 'editProduct.html', {'productList':productList, 'adminName':request.session['adminLogin'], 'currentPage':'editProduct', 'sidebarHeading':'products'})
# Save product data sent from editProduct page
def updateProductData(request):
    receivedData = json.loads(str(request.body, encoding='utf-8'))
    db.Table('PRODUCTS').update_item(
        Key={'docId':receivedData['productId']},
        UpdateExpression='SET description = :newDescription, height = :newHeight, productName = :newName, productImage = :newImage, width = :newWidth, productPriceInfo = :newProductPriceInfo',
        ExpressionAttributeValues={
            ':newDescription':receivedData['description'],
            ':newHeight':receivedData['height'],
            ':newName':receivedData['productName'],
            ':newProductPriceInfo':receivedData['productPriceInfo'],
            ':newImage':receivedData['productImage'],
            ':newWidth':receivedData['width'],
            ':newHeight':receivedData['height'],
        }
    )
    return JsonResponse({'status':'success', 'data':receivedData})