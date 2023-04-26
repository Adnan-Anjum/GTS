# import boto3
# from boto3.dynamodb.conditions import Attr, Key

import uuid

temp=uuid.uuid4().hex
print(temp)

# def update_amount(container_cart):
    
#     # method to get details of that key from product table

#     # Store lid_pricing and container_pricing
#     lid_pricing = {"wooden":10,"nolid":0}
#     container_pricing = {'1':30,"24":25,'48':22}

#     no_of_containers = 0
#     for item in container_cart:
#         no_of_containers = no_of_containers + (item['qnt']*item['set'])
    
#     ppp = 0
#     ind = int(list(container_pricing.keys())[-1])
#     if(ind < no_of_containers):

#         ppp = container_pricing[str(ind)]
#     else:
#         ind = str(int(no_of_containers/24)*24)
#         if ind == "0":
#             ppp = container_pricing['1']
#         else:
#             ppp = container_pricing[ind]

#     for ind,val in enumerate(container_cart):
#         amount = val['qnt']*val['set']*lid_pricing[val['lidType']]
#         amount = amount + (val['qnt']*val['set']*ppp)
#         container_cart[ind]['amount'] = amount


# db = boto3.resource(service_name = 'dynamodb',region_name = 'us-east-1',
#         aws_access_key_id = 'AKIAWUIFHJLFHNQCPCPY',
#         aws_secret_access_key = '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')
# # print(db)
# temp_list=[]
# ob1={
#     'prodId':'76b80f9e030f4ccc9474e3e4ccdee795',
#     'qty':5,
# }

# temp = db.Table('CUSTOMER').get_item(Key={'docId':'f39d8c20235f4b5f89dea74766138748'})['Item']

# temp_list= temp['tempDict']
# print(temp_list['60ml'])
# update_amount(temp_list['60ml'])
# print(temp_list['60ml'])
# # print(temp_list)
# # temp_list.append(ob1)
# # db.Table('CUSTOMER').update_item(
# #                 Key={'docId':'f39d8c20235f4b5f89dea74766138748'},
# #                 UpdateExpression='SET cartItems = :newCartItems',
# #                 ExpressionAttributeValues={
# #                     ':newCartItems':temp_list
# #                 }
# #             )

# # res = dict()
# # for dict in temp_list:
    
# #     if(dict['prodId'] in res.keys()):
# #         res[dict['prodId']].append(dict)
# #     else:
# #         res[dict['prodId']] = [dict]
# # print(res)


