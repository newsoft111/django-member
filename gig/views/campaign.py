from django.shortcuts import redirect, render,get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from gig.models import GigCampaign,GigCampaignOffer,GigCampaignReview
from django.core.paginator import Paginator
from account.views import user_login
from main.views import index
from datetime import datetime, timedelta
import random
import re
from util.views import AddUserPointLog
from payment.views import payment_refund
from account.models import UserShippingAddress


def campaign_list(request):
	seo = {
		'title': "콘디",
	}
	

	category_list = [
		'코스메틱', 
		'미용', 
		'패션/잡화',
		'식품', 
		'생활용품', 
		'출산/육아', 
		'디지털/가전', 
		'스포츠/건강', 
		'반려동물', 
		'맛집', 
		'여행/숙박', 
		'지역/문화', 
		'기타'
	]
	channel_list = ["네이버블로그", "인스타그램", "유튜브", "카페", "네이버포스트", "기타"]
	type_list = ['배송형', '방문형', '기자단','구매형']
	
	q = Q()
	q &= Q(is_paid = True)
	if request.GET.get("category"):
		q &= Q(category = category_list[int(request.GET.get("category"))])
	if request.GET.get("channel"):
		q &= Q(channel = channel_list[int(request.GET.get("channel"))])
	if request.GET.get("type"):
		q &= Q(campaign_type = type_list[int(request.GET.get("type"))])
	if request.GET.get("keyword"):
		q &= Q(subject__icontains = request.GET.get("keyword"))
	
	

	campaign_list =  GigCampaign.objects.filter(q).order_by('-is_item', "-id")
	page        = int(request.GET.get('p', 1))
	pagenator   = Paginator(campaign_list, 10)
	campaign_list = pagenator.get_page(page)
	return render(request, 'gig/campaign/campaign_list.html' ,{
		"seo":seo,
		"campaign_list":campaign_list,
		"category_list":category_list,
		"channel_list":channel_list,
		"type_list":type_list,
	})


def campaign_write(request):
	if not request.user.is_authenticated: #로그인 상태면
		return redirect(user_login)

	if request.method == 'POST':
		campaign_type = request.POST.get("campaign_type")
		category = request.POST.get("category")
		thumbnail = request.FILES['campaign_img']
		subject = request.POST.get("subject")
		provide = request.POST.get("provide")
		guide_line = request.POST.get("guide_line")
		keyword = request.POST.get("keyword")
		product_url = request.POST.get("product_url")
		channel = request.POST.get("channel")
		limit_offer = request.POST.get("limit_offer")
		finished_at = request.POST.get("finished_at")
		item = request.POST.get("item")
		reward = re.sub(r'[^0-9]', '', request.POST.get('reward'))

			
		try:
			campaign = GigCampaign()
			campaign.campaign_type = campaign_type
			campaign.category = category
			campaign.subject = subject
			campaign.channel = channel
			campaign.thumbnail = thumbnail
			campaign.provide = provide
			campaign.guide_line = guide_line
			campaign.keyword = keyword
			campaign.product_url = product_url
			campaign.limit_offer = limit_offer
			campaign.finished_at = datetime.now() + timedelta(days=int(finished_at))
			campaign.reward = reward
			campaign.user = request.user
			campaign.merchant_uid = None
			if item != 'default':
				campaign.is_item = True
				if item == 'recommend':
					campaign.is_recommend = True
			campaign.save()

			campaign = GigCampaign.objects.get(pk=campaign.pk)
			campaign.merchant_uid = str(datetime.now().strftime('%Y%m%d')) + str(campaign.pk) + str(random.randint(10000,99999))
			campaign.save()


			result = '200'
			result_text = campaign.merchant_uid
		except:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'
		

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return render(request, 'gig/campaign/campaign_write.html')


def campaign_update(request, campaign_id):
	try:
		campaign = GigCampaign.objects.get(pk=campaign_id, user=request.user)
	except:
		return redirect(user_login)

	if request.method == 'POST':
		campaign_type = request.POST.get("campaign_type")
		category = request.POST.get("category")
		try:
			thumbnail = request.FILES['campaign_img']
		except:
			thumbnail = None
		subject = request.POST.get("subject")
		provide = request.POST.get("provide")
		guide_line = request.POST.get("guide_line")
		keyword = request.POST.get("keyword")
		product_url = request.POST.get("product_url")
		channel = request.POST.get("channel")
			
		try:
			campaign.campaign_type = campaign_type
			campaign.category = category
			campaign.subject = subject
			campaign.channel = channel
			if thumbnail is not None:
				campaign.thumbnail = thumbnail
			campaign.provide = provide
			campaign.guide_line = guide_line
			campaign.keyword = keyword
			campaign.product_url = product_url
			campaign.save()
			result = '200'
			result_text = '수정이 완료되었습니다.'
		except:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'
		print(result_text)

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return render(request, 'gig/campaign/campaign_update.html', {"campaign_update":campaign})


def campaign_detail(request, campaign_id):
	try:
		campaign = GigCampaign.objects.get(pk=campaign_id)
	except:
		return redirect('/')

	try:
		campaign_offer = GigCampaignOffer.objects.get(campaign=campaign_id, user=request.user)
	except:
		campaign_offer = None
	print(campaign_offer)
	
	q = Q()
	q &= Q(is_paid = True)
	q &= Q(is_item = True)
	q &= Q(is_recommend = True)
	q &= Q(finished_at__gte=datetime.now())
	recommend_campaign_list =  GigCampaign.objects.filter(q).order_by("-id")

	return render(request, 'gig/campaign/campaign_detail.html', {"campaign_detail":campaign, "campaign_offer":campaign_offer, "recommend_campaign_list":recommend_campaign_list})


def campaign_delete(request, campaign_id):
	try:
		campaign = GigCampaign.objects.get(pk=campaign_id, user=request.user)
	except:
		campaign = None

	if campaign is not None:
		if payment_refund(campaign.merchant_uid,'캠페인 환불 요청'):
			campaign.delete()
			result = '200'
			result_text = '삭제가 완료되었습니다.'
		else:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'
	else:
		result = '201'
		result_text = '알수없는 오류입니다. 다시시도 해주세요.'

	result = {'result': result, 'result_text': result_text}
	return JsonResponse(result)


def campaign_offer(request,campaign_id):
	if not request.user.is_authenticated: #로그인 상태면
		return redirect(user_login)
	
	if request.method == 'POST':
		shipping_address_id = request.POST.get("shipping_address")
		appeal = request.POST.get("appeal")
		sns_url = request.POST.get("sns_url")

		try:
			shipping_address = UserShippingAddress.objects.get(pk=shipping_address_id)
		except:
			shipping_address = None

		try:
			campaign = GigCampaign.objects.get(pk=campaign_id)
		except:
			campaign = None

		if campaign is not None:
			if request.user in campaign.offer_user.all():
				campaign.offer_user.remove(request.user)
				result = '200'
				result_text = "캠페인 신청 취소가 완료되었습니다."
			else:
				if shipping_address is not None:
					campaign_offer = GigCampaignOffer()
					campaign_offer.campaign = campaign
					campaign_offer.user = request.user
					campaign_offer.shipping_address = shipping_address
					campaign_offer.appeal = appeal
					campaign_offer.sns_url = sns_url
					campaign_offer.save()

					result = '200'
					result_text = "캠페인 신청이 완료되었습니다."
				else:
					result = '201'
					result_text = '알수없는 오류입니다. 다시시도 해주세요.'
		else:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return redirect(index)
	


def campaign_favorite(request):
	if not request.user.is_authenticated: #로그인 상태면
		result = '201'
		result_text = '로그인이 필요합니다.'
		
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)   
	if request.method == 'POST':
		try:
			campaign = GigCampaign.objects.get(id=request.POST.get("campaign_id"))
		except:
			campaign = None

		
		if campaign is not None:
			if request.user in campaign.favorite_user.all():
				campaign.favorite_user.remove(request.user)
				result = '200'
				result_text = False #좋아요 삭제
			else:
				campaign.favorite_user.add(request.user)
				result = '200'
				result_text = True #좋아요 추가
		else:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'
		
	else:
		result = '201'
		result_text = '알수없는 오류입니다. 다시시도 해주세요.'
	result = {'result': result, 'result_text': result_text}
	return JsonResponse(result)


def campaign_pick(request, campaign_id):
	if not request.user.is_authenticated: #로그인 상태면
		return redirect(user_login)

	q = Q()
	q &= Q(campaign_id = campaign_id)
	campaign_offer_list = GigCampaignOffer.objects.filter(q).order_by("-is_picked","-id")
	q &= Q(is_picked = True)
	campaign_picked_count = GigCampaignOffer.objects.filter(q).count()

	try:
		is_mine = campaign_offer_list[0].campaign.user
	except:
		is_mine = None

	if is_mine != request.user:
		return redirect(index)

	if request.method == 'POST':
		offer_id = request.POST.get("offer_id")

		try:
			campaign_offer = GigCampaignOffer.objects.get(id=offer_id)
		except:
			campaign_offer = None
		
		if campaign_offer is not None:
			try:
				campaign_offer.is_picked = True
				campaign_offer.save()
				result = '200'
				result_text = '체험단 선정이 완료되었습니다.'
			except:
				result = '201'
				result_text = '알수없는 오류입니다. 다시시도 해주세요.'
		else:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return render(request, 'gig/campaign/campaign_pick.html',{"campaign_offer_list":campaign_offer_list,"campaign_picked_count":campaign_picked_count})
	

def campaign_review(request,campaign_id):
	if not request.user.is_authenticated: #로그인 상태면
		return redirect(user_login)

	try:
		campaign_offer = GigCampaignOffer.objects.get(user=request.user,campaign=campaign_id,is_picked=True)
	except:
		campaign_offer = None
	
	if campaign_offer is not None:
		review_url = request.POST.get("review_url")
		try:
			campaign_review = GigCampaignReview()
			campaign_review.offer = campaign_offer
			campaign_review.review_url = review_url
			campaign_review.save()
			result = '200'
			result_text = '리뷰등록이 완료되었습니다.'
		except Exception as e:
			print(e)
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return redirect(index)


def campaign_confirm(request,review_id):
	if not request.user.is_authenticated: #로그인 상태면
		return redirect(user_login)

	try:
		campaign_review = GigCampaignReview.objects.get(pk=review_id)
	except:
		campaign_review = None

	if campaign_review.offer.campaign.user == request.user:
		try:
			campaign_review.is_confirm = True
			campaign_review.save()
			result = '200'
			result_text = '리뷰 확인이 완료되었습니다.'
		except Exception as e:
			print(e)
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'
	else:
		result = '201'
		result_text = '알수없는 오류입니다. 다시시도 해주세요.'

	result = {'result': result, 'result_text': result_text}
	return JsonResponse(result)