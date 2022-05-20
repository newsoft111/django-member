from django.shortcuts import resolve_url
from iamport import Iamport
from django.http import JsonResponse
from gig.models import GigCampaign
from .models import Payment
import json
from django.db.models import Q
import re
from util.views import AddUserPointLog
# Create your views here.

iamport = Iamport(
	imp_key='9233357849957397', 
	imp_secret='qh88zbQvsbOONwGcvCNfWJX7dbfPn70Np9WYkMtNYiCLPiYlVLASvyZJKfz7nzVMIRL3EfQCysonLmIG'
)

def campaign_payment_check(request):
	imp_uid = request.POST.get("imp_uid")
	response = json.dumps(iamport.find(imp_uid=imp_uid))
	payment_json_data = json.loads(response)
	merchant_uid = payment_json_data['merchant_uid']

	campaign_pk = merchant_uid[8:-5]
	print(campaign_pk)
	print(merchant_uid)

	try:
		campaign = GigCampaign.objects.get(pk = campaign_pk, merchant_uid = merchant_uid)
	except:
		campaign = None
	
	if campaign is not None:
		recruit_day = campaign.started_at - campaign.finished_at
		recruit_day = recruit_day.days*-1
		limit_offer = campaign.limit_offer
		reward = int(campaign.reward) * int(limit_offer)

		item_price = 0
		if campaign.is_item:
			item_price = item_price+10000
			if campaign.is_recommend:
				item_price = item_price+20000
		
		campaign_price = (recruit_day-3)*2000+(limit_offer*5000)+reward+item_price+100-int(re.sub(r'[^0-9]', '', request.POST.get('use_point')))

		if payment_json_data['amount'] == campaign_price:
			payment = Payment()
			payment.user = request.user
			payment.pay_method = payment_json_data['pay_method']
			payment.pg = payment_json_data['pg_provider']
			payment.paid_amount = payment_json_data['amount']
			payment.merchant_uid = payment_json_data['merchant_uid']
			payment.imp_uid = payment_json_data['imp_uid']
			payment.apply_num = payment_json_data['apply_num']
			payment.save()

			if AddUserPointLog(request.user, '캠페인 등록', -int(request.POST.get('use_point'))):
				campaign.is_paid = True
				campaign.save()

				result = '200'
				result_text = "결제가 완료되었습니다."
				result = {'result': result, 'result_text': result_text, "next_url":resolve_url('CampaignDetail', campaign_pk)}
				return JsonResponse(result)
			else:
				result = '201'
				result_text = "알수없는 오류입니다.1 다시시도 해주세요."
		else:
			result = '201'
			result_text = "알수없는 오류입니다.2 다시시도 해주세요."
	else:
		result = '201'
		result_text = "알수없는 오류입니다.3 다시시도 해주세요."


	result = {'result': result, 'result_text': result_text}
	return JsonResponse(result)

def payment_refund(merchant_uid, memo):
	print(merchant_uid)
	try:
		response = iamport.cancel(memo, merchant_uid=merchant_uid)
		payment = Payment.objects.get(merchant_uid=merchant_uid)
		payment.is_refund = True
		payment.save()
		result = True
	except Iamport.ResponseError as e:
		print(e.code)
		print(e.message)  # 에러난 이유를 알 수 있음
		result = False
	except Iamport.HttpError as http_error:
		print(http_error.code)
		print(http_error.reason) # HTTP not 200 에러난 이유를 알 수 있음
		result = False

	return result