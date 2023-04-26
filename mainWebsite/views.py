from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, response, QueryDict,HttpResponseRedirect
import json
import smtplib
from django.urls import reverse
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

def temp_func(x):
    # print(db)
    table=db.Table('CUSTOMER')
    all_user=table.scan()
    # print()
    return render(x,"temp.html")

# Constants
UNI_DOC_ID = '89f955f222844bb79b60afc27fc99314'

# DynamoDB Cursor
db = boto3.resource(service_name = 'dynamodb',region_name = 'us-east-1',
        aws_access_key_id = 'AKIAWUIFHJLFHNQCPCPY',
        aws_secret_access_key = 'boUoP1NaUl4KnfWB8kjAs4UJtScVpd8CxgokahL5')

# Create your views here.
def home(request):
    # candleContainersQuery = db.Table('PRODUCTS').query(
    #     IndexName='productCategory-index',
    #     KeyConditionExpression=Key('productCategory').eq('candleContainers')
    # )
    # fragranceOilsQuery = db.Table('PRODUCTS').query(
    #     IndexName='productCategory-index',
    #     KeyConditionExpression=Key('productCategory').eq('fragranceOils')
    # )
    # waxesQuery = db.Table('PRODUCTS').query(
    #     IndexName='productCategory-index',
    #     KeyConditionExpression=Key('productCategory').eq('waxes')
    # )
    # candleWicksQuery = db.Table('PRODUCTS').query(
    #     IndexName='productCategory-index',
    #     KeyConditionExpression=Key('productCategory').eq('candleWicks')
    # )
    # return render(request, 'index.html', {'candleContainersCount':candleContainersQuery['Count'], 'fragranceOilsCount':fragranceOilsQuery['Count'],
    #                                         'waxesCount':waxesQuery['Count'], 'candleWicksCount':candleWicksQuery['Count']})
    loggedInCustomerName = ''
    loggedInCustomerId = ''
    if (request.session.get('customerLogin') != None):
        loggedInCustomerName = request.session['customerLogin']
        loggedInCustomerId = request.session['customerLoginId']
    return render(request, 'index.html', {'loggedInCustomerName':loggedInCustomerName, 'loggedInCustomerId':loggedInCustomerId})

# Login/Register page
def login(request):
    loggedInCustomerName = ''
    loggedInCustomerId = ''
    if (request.session.get('customerLogin') != None):
        loggedInCustomerName = request.session['customerLogin']
        loggedInCustomerId = request.session['customerLoginId']
        return redirect('/')
    return render(request, 'customerLogin.html')
# Login an old website user
def loginUser(request):
    receivedData = json.loads(str(request.body, encoding='utf-8'))
    customerQuery = db.Table('CUSTOMER').query(
        IndexName='email-index',
        KeyConditionExpression=Key('email').eq(receivedData['email'])
    )
    if customerQuery['Count'] == 0:
        return JsonResponse({'status':'notFound'})
    else:
        customerData = customerQuery['Items'][0]
        if (hashlib.md5(receivedData['password'].encode()).hexdigest() == customerData['password']):
            request.session['customerLogin'] = customerData['name'].split()[0]
            request.session['customerLoginId'] = customerData['docId']
            request.session.modified = True
            return JsonResponse({'status':'success'})
    return JsonResponse({'status':'wrongPass'})

# Register a new website user
def registerUser(request):
    receivedData = QueryDict(request.body).dict()
    del receivedData['csrfmiddlewaretoken']
    receivedData['docId'] = uuid.uuid4().hex
    receivedData['password'] = hashlib.md5(receivedData['password'].encode()).hexdigest()
    receivedData['cartItems'] = []
    receivedData['inchProdList'] = []
    # productQuery = db.Table('PRODUCTS').query(IndexName='productCategory-index',KeyConditionExpression=Key('productCategory').eq('candleContainers'))
    # productQuery = productQuery['Items']
    # tempDict = {}
    # for item in productQuery:
    #     tempDict[item['name']] = []
        
    receivedData['tempDict']={}
    db.Table('CUSTOMER').put_item(Item=receivedData)
    request.session['customerLogin'] = receivedData['name'].split()[0]
    request.session['customerLoginId'] = receivedData['docId']
    request.session.modified = True
    return redirect('/')
# Logout Customer
def logoutUser(request):
    del request.session['customerLogin']
    request.session.modified = True
    return JsonResponse({'status':'success'})

# Customer cart page


def cart(request):
    loggedInCustomerName = ''
    loggedInCustomerId = ''
    if (request.session.get('customerLogin') != None):
        loggedInCustomerName = request.session['customerLogin']
        loggedInCustomerId = request.session['customerLoginId']
    customerData = db.Table('CUSTOMER').get_item(Key={'docId':loggedInCustomerId})['Item']
    cartItemList = []
    for cartItem in customerData['cartItems']:
        productId = list(cartItem.keys())[0]
        temp = db.Table('PRODUCTS').get_item(Key={'docId':productId})['Item']
        temp['cartQuantity'] = cartItem[productId]
        cartItemList.append(temp)
    total_price_list=[]
    if cartItemList!=[]:
        total_price=''
        for obj in cartItemList:
            temp_priceinfo=obj['productPriceInfo']
            unit=''
            try:
                unit=temp_priceinfo[0].split(' ')[1]
            except Exception as e:
                unit='piece'
                # print(e)
            obj['unit']=unit
            prod_qnt=obj['cartQuantity']
            new_product_lsit=[]
            for price_qnt in obj['productPriceInfo']:
                if price_qnt!='':
                    new_product_lsit.append(price_qnt)
            price_cond_dict={}
            # unit=""
            # if 'piece' in new_product_lsit[0]:
            #     unit='piece'
            # elif 'ml' in new_product_lsit[0]:
            #     unit='ml'
            # elif 'kg' in new_product_lsit[0]:
            #     unit='kg'
            # print(new_product_lsit)
            if len(new_product_lsit)>1:
                for price in new_product_lsit:
                    qnt_cond=price.split(' ')[0]    
                    p_a_q=''
                    for a in price.split('-')[1]:
                        if a.isdigit() or a=='.':
                            p_a_q=f'{p_a_q}{a}'
                    price_acc_qnt=float(p_a_q)
                    price_cond_dict.update({int(qnt_cond):price_acc_qnt})
            else:
                for a in new_product_lsit:
                    if 'Set of' in a:
                        obj['unit']='Set'
                        qnt_cond=a.split(' ')[2]
                        p_a_q=''
                        for b in a.split('-')[1]:
                            if b.isdigit():
                                p_a_q=f'{p_a_q}{b}'
                        price_acc_qnt=float(p_a_q)
                        price_cond_dict.update({int(qnt_cond):price_acc_qnt})
                    else:
                        obj['unit']='1 piece'
                        qnt_cond=1
                        p_a_q=''
                        for b in a:
                            if b.isdigit():
                                p_a_q=f'{p_a_q}{b}'
                        price_acc_qnt=float(p_a_q)
                        price_cond_dict.update({int(qnt_cond):price_acc_qnt})
            # print(price_cond_dict)
            # print(obj['unit'])
            conditionSatisfied=0
            if obj['unit']!='ml':
                if obj['unit']=='Set':
                    price_of_one_set=list(price_cond_dict.values())[0]
                    total_price=int(prod_qnt)*price_of_one_set
                    total_price_list.append({'price':total_price,'name':obj['productName']})
                else:
                    list_of_condition=list(price_cond_dict.keys())
                    if prod_qnt<list_of_condition[-1]:
                        for a in range(len(list_of_condition)):
                            if (prod_qnt>=list_of_condition[a] or prod_qnt<list_of_condition[a]) and prod_qnt<list_of_condition[a+1]:
                                conditionSatisfied=list_of_condition[a]
                                break
                    else:
                        conditionSatisfied=list_of_condition[-1]
                    matched_price=price_cond_dict[conditionSatisfied]
                    total_price=f'{int(prod_qnt)*matched_price}'
                    total_price_list.append({'price':total_price,'name':obj['productName']})
            elif obj['unit']=='ml':
                list_of_condition=list(price_cond_dict.keys())
                list_of_condition.remove(1)
                list_of_condition.append(1000)
                # print(list_of_condition)
                one_value=0
                if prod_qnt<list_of_condition[-1]:
                    for a in range(len(list_of_condition[:-1])): 
                        if (prod_qnt>=list_of_condition[a] or prod_qnt<list_of_condition[a]) and prod_qnt<list_of_condition[a+1]:
                            one_value=int(price_cond_dict[list_of_condition[a]]/list_of_condition[a])
                            conditionSatisfied=list_of_condition[a]
                            break
                else:
                    conditionSatisfied=1
                    one_value=price_cond_dict[1]/1000
                matched_price=one_value*int(prod_qnt)
                total_price=f'{matched_price}'
                # print(f'total price : {total_price}')
                total_price_list.append({'price':total_price,'name':obj['productName']})
                # print(total_price_list)
                # print(cartItemList)

# =? FOR CONTAINERS PRODUCT

    customerData=db.Table('CUSTOMER').get_item(Key={'docId':loggedInCustomerId})['Item']
    containerProducts=customerData['tempDict']
    # productImage={'60ml':{'white':'hi','black':'by','amber':'why','clear':'guy'},'100ml':{'white':'hi','black':'by','amber':'why','clear':'guy'},'200ml':{'white':'hi','black':'by','amber':'why','clear':'guy'},'300ml':{'white':'hi','black':'by','amber':'why','clear':'guy'}}
    # for key,item in containerProducts.items():
    #     for obj in item:
    #         image=productImage[key][obj['color']]
    #         obj['image']=image
    # print(containerProducts)
    count=0
    for a in containerProducts:
        if len(containerProducts[a])>0:
            count=count+1
            break
    if count==0:
        containerProducts=[]
    # totalPrieDict={}
    # for key in containerProducts.keys():
    #     if containerProducts[key]!=[]:
    #         totalQnt=0
    #         numOfLid=0
    #         for each in containerProducts[key]:
    #             qnt=int(each['set'])*int(each['qnt'])
    #             totalQnt=totalQnt+qnt
    #             if each['lidType']=='wooden':
    #                 numOfLid=numOfLid+qnt
    #             elif each['lidType']=='nolid':
    #                 pass
            

# =? FOR INCHES PRODUCT
    inches_product=[]
    if customerData['inchProdList']!=[]:
        price_list={1:0.75,2:0.80,3:0.85,4:0.90,5:1.0,6:1.25,7:1.50}
        for each in customerData['inchProdList']:
            item=db.Table('PRODUCTS').get_item(Key={'docId':each['p_id']})['Item']
            m_p=price_list[each['size']]
            each_inches_price=m_p*int(each['qnt'])
            inches_product.append({'name':item['name'],'total_price':each_inches_price,'productPriceInfo':item['productPriceInfo'],'cartQuantity':each['qnt'],'size':each['size']})
            # print(each_inches_price)
    
    # print(inches_product)
    return render(request, 'cart.html', {'loggedInCustomerName':loggedInCustomerName, 'loggedInCustomerId':loggedInCustomerId, 'cartItemId':customerData['cartItems'], 'cartItemList':cartItemList,'total_product_price':total_price_list,'containerProducts':containerProducts,'inchesProduct':inches_product})  
# Add new item to cart

# =? FUNCTION FOR UPDATE FOR CONTAINERS
def update_amount(container_cart,size):
    # id='4dea5a72e09a4e82809bdb7ec98d7784'
    # method to get details of that key from product table
    # Store lid_pricing and container_pricing
    productQuery = db.Table('PRODUCTS').query(IndexName='productCategory-index',KeyConditionExpression=Key('productCategory').eq('candleContainers'))
    for a in productQuery['Items']:
        if a['name']==size:
            container_pricing=a['productPriceInfo']
            # lid_pricing = a['lidPrice']
    no_of_containers = 0
    for item in container_cart:
        no_of_containers = no_of_containers + (item['qnt']*item['set'])
    
    ppp = 0
    container_keys = sorted([eval(i)for i in list(container_pricing.keys())])
            
    if(no_of_containers > container_keys[-1]):
        ppp = container_keys[-1]
    else:
        for ind,val in enumerate(container_keys[:-1]):
            if container_keys[ind] <= no_of_containers < container_keys[ind+1]:
                ppp = val

    amount=0
    for ind,val in enumerate(container_cart):
        # amount = val['qnt']*val['set']*container_pricing[str(ppp)]
        amount = amount + (val['qnt']*val['set']*container_pricing[str(ppp)])
        container_cart[ind]['amount'] = amount
    # ind = int(list(container_pricing.keys())[-1])
    # if(ind < no_of_containers):
    #     ppp = container_pricing[str(ind)]
    # else:
    #     keys_list = list(container_pricing.keys())
    #     for ind,val in enumerate(keys_list[0:-1]):
    #         if(int(keys_list[ind])<=no_of_containers<int(keys_list[ind+1])):
    #             ppp = container_pricing[val]
            
    # for ind,val in enumerate(container_cart):
    #     amount = val['qnt']*val['set']*lid_pricing[val['lidType']]
    #     amount = amount + (val['qnt']*val['set']*ppp)
    #     container_cart[ind]['amount'] = amount

# =? ADD TO CART FOR CONTAINERS 
def test(request):
    loggedInCustomerName = ''
    loggedInCustomerId = ''
    if (request.session.get('customerLogin') != None):
        loggedInCustomerName = request.session['customerLogin']
        loggedInCustomerId = request.session['customerLoginId']
    customerData=db.Table('CUSTOMER').get_item(Key={'docId':loggedInCustomerId})['Item']
    temp_dict=customerData['tempDict']
    # print(temp_dict)
    set=request.POST.get('set','')
    color=request.POST.get('color','')
    # lid=request.POST.get('lid','')
    qnt=request.POST.get('set_qnt','')
    size=request.POST.get('size','')
    # print(size)
    if size not in temp_dict.keys():
        temp_dict[size] = []
    if temp_dict[size]!=[]:
        count=0
        for each in temp_dict[size]:
            if each['color']==color and int(each['set'])==int(set):
                each['qnt']=int(each['qnt'])+int(qnt)
                break
            else:
                count=count+1
        if count==len(temp_dict[size]):
            temp_dict[size].append({'set':int(set),'color':color,'qnt':int(qnt),'amount':0})
    else:
        temp_dict[size].append({'set':int(set),'color':color,'qnt':int(qnt),'amount':0})
    
    update_amount(temp_dict[size],size)
    db.Table('CUSTOMER').update_item(Key={'docId':loggedInCustomerId},UpdateExpression='SET tempDict = :containerProd',ExpressionAttributeValues={':containerProd':temp_dict})
    
    # print(temp_dict)
    return HttpResponseRedirect(reverse('main:productsByCategory',kwargs={"category":"candleContainers"}))



# =? FOR INCHES PRODUCT AND MAIN
only_inches_product=[]
size_found=[]
def addToCart(request):
    try:
        receivedData = json.loads(str(request.body, encoding='utf-8'))
        # print(receivedData['customerId'])
        if receivedData['inch_input']!='not inch':
            customer_data = db.Table('CUSTOMER').get_item(Key={'docId':receivedData['customerId']})['Item']
            # print(customer_data['inchProdList'])
            only_inches_product = customer_data['inchProdList']
            # print(only_inches_product)
            if len(only_inches_product)==0:
                size_found.append(int(receivedData['inch_input']))
                only_inches_product.append({'size':int(receivedData['inch_input']),'qnt':int(receivedData['cartQuantity']),'p_id':receivedData['productId']})
            else:
                for inch_obj in only_inches_product:
                    if int(receivedData['inch_input']) == int(inch_obj['size']):
                        inch_obj['qnt']=int(inch_obj['qnt'])+int(receivedData['cartQuantity'])
                        break
                    else:
                        if int(receivedData['inch_input']) in size_found:
                            pass
                        else:
                            size_found.append(int(receivedData['inch_input']))
                            only_inches_product.append({'size':int(receivedData['inch_input']),'qnt':int(receivedData['cartQuantity']),'p_id':receivedData['productId']})
                            break
        # print(only_inches_product)
            # prod_id=int(receivedData['productId']) 
            # qntity=int(receivedData['cartQuantity'])
            # size=int(receivedData['inch_input']) 
            # print(prod_id)
            # print(size)
            # print(qntity)
        customerData = db.Table('CUSTOMER').get_item(Key={'docId':receivedData['customerId']})['Item']
        # print(customerData)
        # print(customerData)
        if receivedData['productId']!='b916855218f846968b11af5030e74ca7':
            foundFlag = 0
            for cartItem in customerData['cartItems']:
                if receivedData['productId'] in list(cartItem.keys()):
                    foundFlag = 1
                    cartItem[receivedData['productId']] = int(cartItem[receivedData['productId']]) + int(receivedData['cartQuantity'])
            if not foundFlag:
                customerData['cartItems'].append({receivedData['productId']:int(receivedData['cartQuantity'])})
            db.Table('CUSTOMER').update_item(
                Key={'docId':receivedData['customerId']},
                UpdateExpression='SET cartItems = :newCartItems',
                ExpressionAttributeValues={
                    ':newCartItems':customerData['cartItems']
                }
            )
        else:
            db.Table('CUSTOMER').update_item(
                Key={'docId':receivedData['customerId']},
                UpdateExpression='SET inchProdList = :inches_cart_item',
                ExpressionAttributeValues={
                    ':inches_cart_item':[]
                }
            )

            db.Table('CUSTOMER').update_item(
                Key={'docId':receivedData['customerId']},
                UpdateExpression='SET inchProdList = :inches_cart_item',
                ExpressionAttributeValues={
                    ':inches_cart_item':only_inches_product
                }
            )
            # print(customerData['inchProdList'])
        # print(customerData)
        # print(customerData['inchProdList'])
        return JsonResponse({'status':'success'})
    except:
        return JsonResponse({'status':'failed'})
# =? AFTER CHECKOUT 
def afterCheckout(request):
    loggedInCustomerName = ''
    loggedInCustomerId = ''
    if (request.session.get('customerLogin') != None):
        loggedInCustomerName = request.session['customerLogin']
        loggedInCustomerId = request.session['customerLoginId']
    amount=request.POST.get('finalAmountInp','')
    # print(amount)
    # Order= db.Table('ORDERS').scan(Select='ALL_ATTRIBUTES',FilterExpression=Attr('customerId').eq(loggedInCustomerId) & Attr('orderDate').eq('')) 
    # print(len(Order['Items']))
    return render(request,'checkOut.html',{'loggedInCustomerName':loggedInCustomerName, 'loggedInCustomerId':loggedInCustomerId,'totalPayableAmount':amount})

# =? Checkout cart items

# totalPayableAmount=0
def checkoutCartItems(request):
    try:
        receivedData = json.loads(str(request.body, encoding='utf-8'))
        receivedData['docId'] = uuid.uuid4().hex
        receivedData['orderTime'] = Decimal(str(receivedData['orderTime']))
        receivedData['orderTimestamp'] = Decimal(str(receivedData['orderTimestamp']))
        receivedData['orderAmount'] = Decimal(str(receivedData['orderAmount']))
        # global totalPayableAmount
        # totalPayableAmount=receivedData['orderAmount']
        # print(totalPayableAmount)
        # print(type(receivedData['inchesCart']))
        
        db.Table('UNIVERSAL').update_item(
            Key={'docId':UNI_DOC_ID},
            UpdateExpression='ADD totalOrders :newTotalOrders',
            ExpressionAttributeValues={
                ':newTotalOrders':1,
            }
        )   
        customerData=db.Table('CUSTOMER').get_item(Key={'docId':receivedData['customerId']})['Item']
        receivedData['cartItemId']=customerData['cartItems']
        receivedData['inchesCart']=customerData['inchProdList']
        receivedData['containerCart']=customerData['tempDict']

        db.Table('ORDERS').put_item(Item=receivedData)

        db.Table('CUSTOMER').update_item(
            Key={'docId':receivedData['customerId']},
            UpdateExpression='SET cartItems = :newCartItems, tempDict = :newContainerItems, inchProdList= :newInchProd',
            ExpressionAttributeValues={
                ':newCartItems':[],
                ':newContainerItems':{},
                ':newInchProd':[]
            }
        )

        # db.Table('CUSTOMER').update_item(
        #     Key={'docId':receivedData['customerId']},
        #     UpdateExpression='SET tempDict = :newContainerItems, inchProdList=:newInchProd , ',
        #     ExpressionAttributeValues={
        #         ':newContainerItems':{}
        #     }
        # )
        # db.Table('CUSTOMER').update_item(
        #     Key={'docId':receivedData['customerId']},
        #     UpdateExpression='SET inchProdList = :newInchProd',
        #     ExpressionAttributeValues={
        #         ':newInchProd':[]
        #     }
        # )
        return JsonResponse({'status':'success','orderAmount':receivedData['orderAmount']})
    except:
        return JsonResponse({'status':'failed'})

# Shop Page
def shop(request):
    productQuery = db.Table('PRODUCTS').scan()
    productList = productQuery['Items']
    while 'LastEvaluatedKey' in productQuery:
        productQuery = db.Table('PRODUCTS').scan(
            ExclusiveStartKey=productQuery['LastEvaluatedKey']
        )
        productList.extend(productQuery['Items'])
    loggedInCustomerName = ''
    loggedInCustomerId = ''
    if (request.session.get('customerLogin') != None):
        loggedInCustomerName = request.session['customerLogin']
        loggedInCustomerId = request.session['customerLoginId']
    return render(request, 'productsByCategory.html', {'productList':productList, 'currentPage': 'fullShop', 'loggedInCustomerName':loggedInCustomerName, 'loggedInCustomerId':loggedInCustomerId})
    
sub_category={
    'candleContainers':['Amber','White','Black','Clear','Frost'],
    'waxes':['Bees','Soy','Paraffin','Gel'],
    'fragranceOils':['Angel Breath','Crackling Birch','Caramel','Citrus','French Vanilla','Crème Brûlée']
}
def productsBySubcategory(request,category):
    loggedInCustomerName = ''
    loggedInCustomerId = ''
    if (request.session.get('customerLogin') != None):
        loggedInCustomerName = request.session['customerLogin']
        loggedInCustomerId = request.session['customerLoginId']
    productQuery = db.Table('PRODUCTS').query(IndexName='productCategory-index',KeyConditionExpression=Key('productCategory').eq('candleContainers'))
    data={
        'set':[],
        'color':[],
        'lid':[],
        'size':category,
        'loggedInCustomerName':loggedInCustomerName,
        'loggedInCustomerId':loggedInCustomerId

    }
    for a in productQuery['Items']:
        if a['name']==category:
            data['set']=list(a['productPriceInfo'].keys())
            data['lid']=list(a['lidPrice'].keys())
            data['color']=a['color']

    # print(data)
    # print(category)
    return render(request,'ContainerATC.html',data)
    # val=request.GET.get('adnan','')
    # print(val)
    # productQuery = db.Table('PRODUCTS').query(IndexName='productCategory-index',KeyConditionExpression=Key('productCategory').eq('candleContainers'))
    # size=request.GET.get('size_val','')
    # temp_str=f'{size} {category}'
    # new_product_list=[]
    # for a in productQuery['Items']:
    #     if temp_str in a['productName']:
    #         new_product_list.append(a)
    # print(size)
    # print(category)
    # loggedInCustomerName = ''
    # loggedInCustomerId = ''
    # if (request.session.get('customerLogin') != None):
    #     loggedInCustomerName = request.session['customerLogin']
    #     loggedInCustomerId = request.session['customerLoginId']
    
    # if productQuery['ScannedCount'] == 0:
    #     return redirect('/')
    # return render(request, 'productsByCategory.html', {'productList':new_product_list, 'currentPage': category, 'loggedInCustomerName':loggedInCustomerName, 'loggedInCustomerId':loggedInCustomerId})

def productsByCategory(request, category):
    loggedInCustomerName = ''
    loggedInCustomerId = ''
    if (request.session.get('customerLogin') != None):
        loggedInCustomerName = request.session['customerLogin']
        loggedInCustomerId = request.session['customerLoginId']
    if category=='candleContainers':
        productQuery = db.Table('PRODUCTS').query(IndexName='productCategory-index',KeyConditionExpression=Key('productCategory').eq('candleContainers'))
        containerSize={
            'size':[],
            'loggedInCustomerName':loggedInCustomerName, 
            'loggedInCustomerId':loggedInCustomerId
        }
        for a in productQuery['Items']:
            containerSize['size'].append(a['name'])
        # print(containerSize)
        # productQuery = db.Table('PRODUCTS').query(IndexName='productCategory-index',KeyConditionExpression=Key('productCategory').eq(category))
        # temp_dic={'cat':[]}
        # for a in sub_category['candleContainers']:
        #     img=''
        #     temp_name=f'60 ML {a}'
        #     for obj in productQuery['Items']:
        #         if temp_name in obj['productName']:
        #             img=obj['productImage']
        #             des=obj['description']
        #             break
        #     temp_dic['cat'].append({'image':img,'name':a,'description':des})
        return render(request,"sub_category.html",containerSize)
    

    productQuery = db.Table('PRODUCTS').query(
        IndexName='productCategory-index',
        KeyConditionExpression=Key('productCategory').eq(category)
    )
    for obj in productQuery['Items']:
        temp_priceinfo=obj['productPriceInfo']
        unit=''
        try:
            unit=temp_priceinfo[0].split(' ')[1]
        except Exception as e:
            unit='piece'
            # print(e)
        obj['unit']=unit
        if obj['unit']=='of':
            obj['unit']='Set'
        # print(obj['unit'])
    # print(productQuery['Items'])
    
    # def func_gen():
    #     for a in productQuery['Items']:
    #         yield a['unit']
    # func=func_gen()
    # print(next(func))
    # print(next(func))
    # print(next(func))
    # print(next(func))
    if productQuery['ScannedCount'] == 0:
        return redirect('/')
    else:
        return render(request, 'productsByCategory.html', {'productList':productQuery['Items'], 'currentPage': category, 'loggedInCustomerName':loggedInCustomerName, 'loggedInCustomerId':loggedInCustomerId})
    
# =? USER PROFILE
def userProfile(request,temp):
    tempV=int(temp)
    Customer_details = db.Table('CUSTOMER').scan()
    loggedInCustomerName = ''
    loggedInCustomerId = ''
    current_user_profile={}
    if (request.session.get('customerLogin') != None):
        loggedInCustomerName = request.session['customerLogin']
        loggedInCustomerId = request.session['customerLoginId']
    # print(Customer_details)
    for obj in Customer_details['Items']:
        if loggedInCustomerName in obj['name']:
            current_user_profile['key']=obj

    
    currentCustomerOrder= db.Table('ORDERS').scan(Select='ALL_ATTRIBUTES',FilterExpression=Attr('customerId').eq(loggedInCustomerId))
    # print(currentCustomerOrder['Items'][0])
    current_user_profile['orders']=currentCustomerOrder['Items']
    current_user_profile['loggedInCustomerId']=loggedInCustomerId
    current_user_profile['loggedInCustomerName']=loggedInCustomerName
    current_user_profile['temp']=tempV
    # for a in currentCustomerOrder['Items'][2]['cartItemId']:
    #     print(a)
    # print(loggedInCustomerName)
    # print(current_user_profile)
    # print(current_user_profile['key'])
    # .query(IndexName='productCategory-index',KeyConditionExpression=Key('productCategory').eq(category))
    return render(request,"UserProfile.html",current_user_profile)

# =? SHOW ORDERS 

def showOrders(request,orderId):
    # print(orderId)
    loggedInCustomerName = ''
    loggedInCustomerId = ''
    current_user_profile={}
    if (request.session.get('customerLogin') != None):
        loggedInCustomerName = request.session['customerLogin']
        loggedInCustomerId = request.session['customerLoginId']
    currentCustomerOrder = db.Table('ORDERS').scan(Select='ALL_ATTRIBUTES',FilterExpression=Attr('docId').eq(orderId))['Items'][0]
    
    # print(currentCustomerOrder)

    if currentCustomerOrder['cartItemId'] !=[]:
        for obj in currentCustomerOrder['cartItemId']:
            for each in obj:
                item=db.Table('PRODUCTS').scan(Select='ALL_ATTRIBUTES',FilterExpression=Attr('docId').eq(each))
                # print(each)
                # print(item['Items'][0])
                obj['productName']=item['Items'][0]['productName']
                obj['quantity']=obj[each]
                obj['productImage']=item['Items'][0]['productImage']
                break

    # print(currentCustomerOrder['cartItemId'])
            
    return render(request,'showOrders.html',{'order':currentCustomerOrder,'loggedInCustomerId':loggedInCustomerId,'loggedInCustomerName':loggedInCustomerName})


