import re
from numpy import PINF
from main.views import index
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth
from .models import User, UserPoint, UserWithdraw, UserShippingAddress, UserMessage
from util.views import EmailSender, AddUserPointLog
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.files.base import ContentFile
import base64
from random import randint

from django.conf import settings
# Create your views here.

def user_login(request):
	if request.user.is_authenticated: #로그인 상태면
		return redirect(index)
	if request.method == 'POST':
		email=request.POST.get('email')
		password=request.POST.get('password')

		user = auth.authenticate(request, email=email, password=password)
		print(user)
		if user is not None:
			if user.is_verify:
				if user.is_active:
					auth.login(request, user)
					result = '200'
					result_text = '로그인 성공'
				else:
					result = '201'
					result_text = '탈퇴한 계정입니다.'	
			else:
				verify_email_url = reverse('VerifyEmail')
				result = '201'
				result_text = f"이메일 인증을 완료해주세요.<a href='{verify_email_url}' class='w-100 btn btn-primary mt-3'>인증메일 다시받기</a>"
		else:
			result = '201'
			result_text = '아이디와 비밀번호를 정확히 입력해 주세요.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)        
	else:
		return render(request, 'account/login.html')

def user_logout(request):
	auth.logout(request)
	return redirect(index)

def user_join(request):
	if request.user.is_authenticated:
		return redirect(index)
	if request.method == 'POST':
		email=request.POST.get('email')
		nickname=request.POST.get('nickname')
		password=request.POST.get('password')

		try:
			_email = User.objects.get(email=email)
		except:
			_email = None
		try:
			_nickname = User.objects.get(nickname=nickname)
		except:
			_nickname = None

		if _email is None:
			if _nickname is None:
				if request.POST['password'] ==request.POST['password2']:
					user = User.objects.create_user(
																		email=email,
																		nickname=nickname,
																		password=password,
																	)
					
					if send_auth_mail(email):
						result = '200'
						result_text = "회원가입이 완료되었습니다.<br>가입하신 이메일 주소로 인증 메일을 보내드렸습니다.<br>이메일 인증을 한 후에 정상적인 서비스 이용이 가능합니다."
						AddUserPointLog(user, '회원가입 축하 포인트', 5000)
					else:
						result = '201'
						result_text = '알수없는 오류입니다.<br>다시시도 해주세요.'
				else:
					result = '201'
					result_text = '비밀번호가 일치하지 않습니다.'
			else:
				result = '201'
				result_text = '입력한 닉네임은 이미 사용 중입니다.'
		else:
			result = '201'
			result_text = '입력한 이메일은 이미 사용 중입니다.'
		print(result_text)
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)

	else:
		return render(request, 'account/join.html')

def join_confirm(request, uidb64, token):
	try:
			uid = force_str(urlsafe_base64_decode(uidb64))
			user = User.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
			user = None

	if user is not None:
		if account_activation_token.check_token(user, token):
			user.is_verify = True
			user.save()
			auth.login(request, user)
			message = "인증이 완료되었습니다."
		else:
			message = "이미 인증을 완료했습니다."
	else:
		message = "알수없는 오류입니다. 다시시도 해주세요."
	return render(request, 'main/index.html', {"message":message})

def verify_email(request):
	if request.user.is_authenticated:
		return redirect(index)
	if request.method == 'POST':
		email=request.POST.get('email')

		try:
			_email = User.objects.get(email=email, is_verify=False)
		except:
			_email = None

		if _email is not None and send_auth_mail(email):
			result = '200'
			result_text = f"{email}로 인증 메일을 보내드렸습니다.<br>이메일 인증을 한 후에 정상적인 서비스 이용이 가능합니다."
		else:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)

	else:
		return render(request, 'account/verify_email.html')

def find_passwd(request):
	if request.user.is_authenticated: #로그인 상태면
		return redirect(index)
	if request.method == 'POST':
		email = request.POST.get('email')
		try:
			user = User.objects.get(email = email)
		except:
			user = None

		if user is not None:
			emailContent = render_to_string('email/reset_password.html',{
					'user': user,
					'domain': settings.CURRENT_URL,
					'uid': urlsafe_base64_encode(force_bytes(user.pk)),
					'token': PasswordResetTokenGenerator().make_token(user),
			})

			_result = EmailSender(
				email              = email,
				subject = '[콘디] 비밀번호 재설정 안내 메일입니다.',
				message = emailContent,
				mailType = 'html'
			)
			
			if _result == '200':
				result = '200'
				result_text = '비밀번호 재설정 메일이 전송되었습니다.<br>메일함을 확인해주세요.'
			else:
				result = '201'
				result_text = '알수없는 오류입니다. 다시시도 해주세요.'
		else:
			result = '201'
			result_text = '등록되지 않은 이메일 입니다.'
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)   
	else:
		return render(request, 'account/find_passwd.html')



def reset_passwd(request, uidb64, token):
	try:
		uid = force_str(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None

	if user is not None:
		if PasswordResetTokenGenerator().check_token(user, token):
			if request.method == 'POST':
				new_password = request.POST.get("password")
				password_confirm = request.POST.get("password2")
				if new_password == password_confirm:
					user.set_password(new_password)
					user.save()
					result = '200'
					result_text = '비밀번호 변경이 완료되었습니다.<br>변경하신 비밀번호로 다시 로그인 해주시기 바랍니다.'
				else:
					result = '201'
					result_text = '입력하신 비밀번호가 동일하지 않습니다.'

				result = {'result': result, 'result_text': result_text}
				return JsonResponse(result)
			else:
				return render(request, 'account/reset_passwd.html')
		else:
			return render(request, 'main/index.html', {"message":"이미 사용된 인증메일 입니다."})
	else:
		return render(request, 'main/index.html', {"message":"알수없는 오류입니다. 다시시도 해주세요."})



def send_auth_mail(email):
	try:
		user = User.objects.get(email=email)
	except:
		user = None
	
	if user is not None:
		message = render_to_string('email/auth_email.html', {
			'user': user,
			'domain': settings.CURRENT_URL,
			'uid': urlsafe_base64_encode(force_bytes(user.pk)),
			'token': account_activation_token.make_token(user),
		})

		EmailSender(
			email              = email,
			subject = '[콘디] 이메일 주소 인증을 완료해 주세요.',
			message = message,
			mailType = 'html'
		)
		return True
	else:
		return False



def user_profile(request):
	if not request.user.is_authenticated: #로그인 상태면
		return redirect(index)
	if request.method == 'POST':
		full_name = request.POST.get("full_name")
		phone_number = request.POST.get("phone_number")
		birth_year = request.POST.get("birth_year")
		try:
			if full_name:
				request.user.full_name = full_name
			if phone_number:
				request.user.phone_number = phone_number
			if birth_year:
				request.user.birth_year = birth_year
			request.user.save()
			result = '200'
			result_text = '변경이 완료되었습니다.'
		except:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요..'
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		q = Q()
		q &= Q(user = request.user)
		shipping_address_lsit =  UserShippingAddress.objects.filter(q).order_by('-is_default', '-id')
		return render(request, 'account/mypage/user_profile.html', {"shipping_address_lsit":shipping_address_lsit})


def change_passwd(request):
	if not request.user.is_authenticated: #로그인 상태면
		return redirect(index)
	if request.method == 'POST':
		current_password = request.POST.get("current_password")
		user = request.user
		if check_password(current_password,user.password):
			new_password = request.POST.get("password")
			password_confirm = request.POST.get("password2")
			if new_password == password_confirm:
				user.set_password(new_password)
				user.save()
				result = '200'
				result_text = '비밀번호 변경이 완료되었습니다.<br>변경하신 비밀번호로 다시 로그인 해주시기 바랍니다.'
				auth.logout(request)
			else:
				result = '201'
				result_text = '입력하신 비밀번호가 동일하지 않습니다.'
		else:
			result = '201'
			result_text = '현재 비밀번호가 옳바르지 않습니다.'
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return redirect(index)

	
def add_shipping_address(request):
	if not request.user.is_authenticated: #로그인 상태면
		return redirect(index)
	if request.method == 'POST':
		address_name = request.POST.get("address_name")
		receiver = request.POST.get("receiver")
		zipcode = request.POST.get("zipcode")
		base_address = request.POST.get("base_address")
		detail_address = request.POST.get("detail_address")
		phone_number = request.POST.get("phone_number")
		is_default = request.POST.get("is_default")

		shipping_address = UserShippingAddress() #출금 내역 추가
		shipping_address.user = request.user
		shipping_address.address_name = address_name
		shipping_address.receiver = receiver
		shipping_address.zipcode = zipcode
		shipping_address.base_address = base_address
		shipping_address.detail_address = detail_address
		shipping_address.detail_address = detail_address
		shipping_address.phone_number = phone_number
		
		try:
			q = Q()
			q &= Q(user = request.user)
			shipping_address_list = UserShippingAddress.objects.filter(q)

			if shipping_address_list.count() < 1:
				is_default = True
			if is_default:
				shipping_address_list.update(is_default=False)
				shipping_address.is_default = True

			shipping_address.save()

			result = '200'
			result_text = '배송지 추가가 완료되었습니다.'
		except:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return redirect(index)


def del_shipping_address(request):
	if not request.user.is_authenticated: #로그인 상태면
		return redirect(index)
	if request.method == 'POST':
		address_id = request.POST.get("address_id")
		
		try:
			shipping_address = UserShippingAddress.objects.get(id=address_id)
		except:
			shipping_address = None
		
		if shipping_address is not None:
			shipping_address.delete()
			result = '200'
			result_text = '배송지 삭제가 완료되었습니다.'
		else:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'
		
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return redirect(index)


def user_delete(request):
	if not request.user.is_authenticated: #로그인 상태면
		return redirect(index)
	
	if request.method == 'POST':
		password = request.POST.get("password")
		try:
			user = User.objects.get(email=request.user.email)
		except:
			user = None

		if user is not None:
			if check_password(password,user.password):
				user.is_active = False
				user.save()
				result = '200'
				result_text = '회원탈퇴가 완료되었습니다.<br>이용해주셔서 감사합니다.'
				auth.logout(request)
			else:
				result = '200'
				result_text = '비밀번호를 정확히 입력해 주세요.'
		else:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'


		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return render(request, 'account/mypage/user_delete.html')



def user_point(request):
	if not request.user.is_authenticated: #로그인 상태면
		return redirect(index)

	q = Q()
	q &= Q(user = request.user)
	point_list =  UserPoint.objects.filter(q).order_by('-id')
	page        = int(request.GET.get('p', 1))
	pagenator   = Paginator(point_list, 10)
	point_list = pagenator.get_page(page)



	bank_list = settings.CURRENT_BANK
	return render(request, 'account/mypage/user_point.html', {"point_list":point_list, "bank_list":bank_list})


def user_withdraw(request):
	if not request.user.is_authenticated: #로그인 상태면
		return redirect(index)
	
	if request.method == 'POST':
		bank_name = request.POST.get("bank_name")
		bank_number = request.POST.get("bank_number")
		user_name = request.POST.get("user_name")

		user = request.user
		if user.point>9999:
			if bank_name and bank_number and user_name:
				withdraw_log = UserWithdraw() #출금 내역 추가
				withdraw_log.user = user
				withdraw_log.bank_account = f"{bank_name}|{bank_number}|{user_name}"
				withdraw_log.amount = -user.point
				withdraw_log.save()

				AddUserPointLog(user, '출금신청', -user.point)

				user.point = 0
				user.save()

				
				result = '200'
				result_text = '출금신청이 완료되었습니다.'
			else:
				result = '201'
				result_text = '은행정보를 입력해주세요.'
		else:
			result = '201'
			result_text = '출금은 10,000원 이상 부터 가능합니다.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		q = Q()
		q &= Q(user = request.user)
		withdraw_list =  UserWithdraw.objects.filter(q).order_by('-id')
		page        = int(request.GET.get('p', 1))
		pagenator   = Paginator(withdraw_list, 10)
		withdraw_list = pagenator.get_page(page)

		point_list =  UserPoint.objects.filter(q).order_by('-id')
		page        = int(request.GET.get('p', 1))
		pagenator   = Paginator(point_list, 10)
		point_list = pagenator.get_page(page)

		bank_list = settings.CURRENT_BANK
		return render(request, 'account/mypage/user_withdraw.html', {"withdraw_list":withdraw_list, "point_list":point_list, "bank_list":bank_list})


def user_message(request):
	if not request.user.is_authenticated: #로그인 상태면
		return redirect(index)
	
	if request.method == 'POST':
		message_id = request.POST.get("message_id")
		try:
			message = UserMessage.objects.get(id=message_id)
		except:
			message = None

		if message is not None:
			message.is_read = True
			message.save()

		
			result = '200'
			result_text = '성공'
		else:
			result = '201'
			result_text = '잘못된 요청입니다.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		q = Q()
		q &= Q(user = request.user)
		message_list =  UserMessage.objects.filter(q).order_by('-id')
		page        = int(request.GET.get('p', 1))
		pagenator   = Paginator(message_list, 10)
		message_list = pagenator.get_page(page)

		return render(request, 'account/mypage/user_message.html', {"message_list":message_list})


def reset_user_message(request):
	if not request.user.is_authenticated: #로그인 상태면
		return redirect(index)
	
	if request.method == 'POST':
		try:
			q = Q()
			q &= Q(user = request.user)
			UserMessage.objects.filter(q).update(is_read=True)

			result = '200'
			result_text = '처리완료 되었습니다.'
		except:
			result = '201'
			result_text = '잘못된 요청입니다.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return redirect(index)

def change_user_avater(request):
	if not request.user.is_authenticated: #로그인 상태면
		return redirect(index)
	
	if request.method == 'POST':
		avater = request.POST.get('avater')

		format, imgstr = avater.split(';base64,') 
		ext = format.split('/')[-1] 
		rand_number = str(randint(100000, 999999))
		data = ContentFile(base64.b64decode(imgstr), name=rand_number + '.' + ext) # You can save this as file instance.

		try:
			request.user.avater = data
			request.user.save()
			result = '200'
			result_text = '이미지 변경이 완료되었습니다.'
		except:
			result = '201'
			result_text = '잘못된 요청입니다.'
		
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)

	else:
		return redirect(index)

def user_campaign(request):
	return True

def user_favorite(request):
	return True

def user_review(request):
	return True

