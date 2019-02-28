from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.Authentication import Myauth
from utils.redis_pool import POOL
import redis
from utils.Base_code import Base_statue_code
from course import models
from utils.CommanException import CommonException
import json
import datetime
from django.core.exceptions import ObjectDoesNotExist
from utils.pay import AliPay

SHOPING_CAR_KEY = "shoping_car_%s_%s"
ACCOUNT_KEY = "account_%s_%s"
REDIS_CONN = redis.Redis(connection_pool=POOL)


# Create your views here.
class Shopping_car(APIView):
    # authentication_classes = [Myauth, ]

    # shopping_car_ %s_ %s: {
    #     id: 1,
    #     title: CMDB,
    #     course_img: xxxxx,
    #     price_policy_dict: {
    #         1: {有效期1个月， 99}
    #
    #       }，
    #     default_price_policy_id: 3
    #
    # }
    def get(self, request):
        res = Base_statue_code()
        try:
            user_id = request.user.id
            shopping_car_key = SHOPING_CAR_KEY % (user_id, "*")
            all_keys = REDIS_CONN.scan_iter(shopping_car_key)
            course_list = []
            for key in all_keys:
                course_info = REDIS_CONN.hgetall(key)
                course_info['price_policy'] = json.loads(course_info['price_policy'])
                course_list.append(course_info)

            res.data = course_list

        except Exception as e:
            res.code = 1033
            res.error = '获取购物车失败'
            return Response(res.dict)
        print(type(res.dict))
        return Response(res.dict)

    def post(self, request):
        res = Base_statue_code()
        try:
            # 获取前端传过来的course_id 和price_policy_id user_id
            # print(request.data)
            # print(request.data)
            # print(type(request.data))
            course_id = request.data.get('course_id', '')
            price_policy_id = request.data.get('price_policy_id', '')
            user_obj = request.user
            # 验证数据的合法性
            course_obj = models.Course.objects.filter(id=course_id).first()

            # 验证课程id是否合法
            if not course_obj:
                res.code = 1030
                res.error = "课程不存在"
                return Response(res.dict)
            price_queryset = course_obj.price_policy.all()

            price_dict = {}
            # 拿到所有的课程的价格
            for price_obj in price_queryset:
                price_dict[price_obj.id] = {
                    "valid_period_text": price_obj.get_valid_period_display(),
                    "price": price_obj.price
                }
            if int(price_policy_id) not in price_dict:
                res.code = 1031
                res.error = "价格不存在"
                return Response(res.dict)
            # 构建数据
            course_info = {
                "id": course_obj.id,
                "title": course_obj.title,
                "course_img": str(course_obj.course_img),
                "price_policy": json.dumps(price_dict, ensure_ascii=False),
                "default_choice": price_policy_id
            }

            # 写入redis
            shopping_car_key = SHOPING_CAR_KEY % (user_obj.id, course_id)
            REDIS_CONN.hmset(shopping_car_key, course_info)
            res.data = "加入购物车成功"
        except Exception as e:
            res.code = 1032
            res.error = "加入购物车失败"
        return Response(res.dict)

    def put(self, request):
        res = Base_statue_code()
        try:
            course_id = request.data.get('course_id', '')
            price_policy_id = request.data.get("price_policy_id", '')
            user_id = request.user.id
            shop_car_key = SHOPING_CAR_KEY % (user_id, course_id)
            if not REDIS_CONN.exists(shop_car_key):
                res.code = 1034
                res.error = "课程不存在"
                return Response(res.dict)
            course_info = REDIS_CONN.hgetall(shop_car_key)

            price_policy_dict = json.loads(course_info['price_policy'])
            if price_policy_id not in price_policy_dict:
                res.code = 1035
                res.error = '价格不合法'
                return Response(res.dict)

            course_info['default_choice'] = price_policy_id
            REDIS_CONN.hmset(shop_car_key, course_info)
            res.data = '价格更新成功'
            print(course_info)
        except Exception as e:
            res.code = 1036
            res.error = '更新失败'
        return Response(res.dict)

    def delete(self, request):
        res = Base_statue_code()
        try:
            course_id = request.data.get('course_id', '')
            user_id = request.user.id
            shop_car_key = SHOPING_CAR_KEY % (user_id, course_id)
            if not REDIS_CONN.exists(shop_car_key):
                res.code = 1037
                res.error = "删除课程不存在"
                return Response(res.dict)
            REDIS_CONN.delete(shop_car_key)
            res.data = '删除成功'
        except Exception as e:
            res.code = 1039
            res.error = "删除失败"
            return Response(res.dict)
        return Response(res.dict)


class AccountView(APIView):
    authentication_classes = [Myauth, ]

    def get_coupons(self, request, course_id=None):
        now = datetime.datetime.utcnow()
        coupon_record_list = models.CouponRecord.objects.filter(
            user=request.user,
            status=0,
            coupon__valid_begin_date__lte=now,
            coupon__valid_end_date__gt=now,
            coupon__content_type_id=10,
            coupon__object_id=course_id

        )
        coupon_dict = {}
        for coupon_record in coupon_record_list:
            coupon_dict[coupon_record.pk] = {
                "name": coupon_record.coupon.name,
                "coupon_type": coupon_record.coupon.get_coupon_type_display(),
                "money_equivalent_value": coupon_record.coupon.money_equivalent_value,
                "off_percent": coupon_record.coupon.off_percent,
                "minimum_consume": coupon_record.coupon.minimum_consume,
                "valid_begin_date": coupon_record.coupon.valid_begin_date.strftime("%Y-%m-%d"),
                "valid_end_date": coupon_record.coupon.valid_end_date.strftime("%Y-%m-%d"),

            }
        return coupon_dict

    def post(self, request):
        user_id = request.user.id
        course_id_list = request.data.get("course_id_list")
        res = Base_statue_code()
        print(2)
        try:
            #  清空缓存，每次进入结算界面只结算当前
            del_list = REDIS_CONN.keys(ACCOUNT_KEY % (user_id, "*"))
            if not len(del_list) == 0:
                REDIS_CONN.delete(*del_list)

            for course_id in course_id_list:
                account_key = ACCOUNT_KEY % (user_id, course_id)
                account_dict = {}
                shopping_car_key = SHOPING_CAR_KEY % (user_id, course_id)
                if not REDIS_CONN.exists(shopping_car_key):
                    raise CommonException('课程不存在在购物车', 1050)
                course_info = REDIS_CONN.hgetall(shopping_car_key)
                course_info['price_policy'] = json.loads(course_info['price_policy'])
                account_dict["course_info"] = course_info

                account_dict["course_coupons"] = self.get_coupons(request, course_id)
                REDIS_CONN.set(account_key, json.dumps(account_dict, ensure_ascii=False))

            REDIS_CONN.set("global_coupon_%s" % user_id, json.dumps(self.get_coupons(request)))
            res.data = 'success'

        except CommonException as e:
            res.code = e.code
            res.error = e.msg
        except Exception as e:
            res.code = 1055
            res.error = '未知错误'
        return Response(res.dict)

    def get(self, request):
        res = Base_statue_code()
        user_id = request.user.id
        account_key = ACCOUNT_KEY % (user_id, '*')
        account_keys = REDIS_CONN.keys(account_key)
        account_list = []
        for key in account_keys:
            account_info = json.loads(REDIS_CONN.get(key))
            account_list.append(account_info)
        res.data = account_list
        return Response(res.dict)


class PaymentView(APIView):
    authentication_classes = [Myauth, ]

    def post(self, request):
        '''
        {
        "courses_info":[
                     {
                      course_id:1,
                      price_policy_id:1,
                      coupon_record_id:2
                     },
                      {
                      course_id:2,
                      price_policy_id:5,
                      coupon_record_id:3
                     }
                     ]

        global_coupon_id:1,
        beli:1000，
        "pay_money":268,

        }
        :param request:
        :return:
        '''
        user = request.user
        courses_info = request.data.get('course_info')
        global_coupon_id = request.data.get('global_coupon_id')
        beli = request.data.get('beli')
        pay_money = request.data.get('pay_money')

        now = datetime.datetime.utcnow()
        res = Base_statue_code()

        try:
            #     循环course_info de 信息
            course_price_list = []

            for course_info in courses_info:
                # 拿到每个字典的所有数据

                course_id = course_info.get('course_id')
                price_policy_id = course_info.get('price_policy_id')
                coupon_record_id = course_info.get('coupon_record_id')

                #       检查数据
                course_obj = models.Course.objects.get(id=course_id)
                if price_policy_id not in [obj.id for obj in course_obj.price_policy.all()]:
                    raise CommonException('价格策略不存在', 1051)
                couponrecord = models.CouponRecord.objects.filter(
                    id=coupon_record_id,
                    user=request.user,
                    status=0,
                    coupon__valid_begin_date__lte=now,
                    coupon__valid_end_date__gte=now,
                    coupon__content_type=10,
                    coupon__object_id=course_id

                ).first()
                if not couponrecord:
                    raise CommonException('课程优惠券有问题', 1052)

                #         计算价格
                course_price = models.PricePolicy.objects.get(id=price_policy_id).price
                coupon_price = self.cal_coupon_price(course_price, couponrecord)
                course_price_list.append(coupon_price)

            g_couponrecord = models.CouponRecord.objects.filter(
                id=global_coupon_id,
                user=request.user,
                status=0,
                coupon__valid_begin_date__lte=now,
                coupon__valid_end_date__gte=now,
                coupon__content_type=10,
                coupon__object_id=None

            ).first()
            if not g_couponrecord:
                raise CommonException('课程通用优惠券有问题', 1053)
            g_price = self.cal_coupon_price(sum(course_price_list), g_couponrecord)

            if beli > request.user.beli:
                raise CommonException('贝里额度不够', 1054)

            final_price = g_price - beli / 10
            print(final_price)
            if final_price < 0:
                final_price = 0
            if final_price != pay_money:
                raise CommonException('实际支付价格与参数价格不一致', 1055)
            import time
            alipay = self.get_alipay()
            query_params = alipay.direct_pay(
                subject="Django课程",  # 商品简单描述
                out_trade_no="x2" + str(time.time()),  # 商户订单号
                total_amount=pay_money,  # 交易金额(单位: 元 保留俩位小数)
            )

            pay_url = "https://openapi.alipaydev.com/gateway.do?{}".format(query_params)

            res.data = "订单创建成功！"
            res.url = pay_url

            # res.data = final_price

        except ObjectDoesNotExist as e:
            res.code = 1050
            res.error = "课程不存在"
        except CommonException as e:
            res.code = e.code
            res.error = e.msg
        except Exception as e:
            res.code = 500
            res.error = str(e)
        return Response(res.dict)

    def cal_coupon_price(self, price, coupon_record):
        coupon_type = coupon_record.coupon.coupon_type
        money_equivalent_value = coupon_record.coupon.money_equivalent_value
        off_percent = coupon_record.coupon.off_percent
        minimum_consume = coupon_record.coupon.minimum_consume
        rebat_price = 0
        if coupon_type == 0:
            rebat_price = price - money_equivalent_value
            if rebat_price < 0:
                rebat_price = 0
        elif coupon_type == 1:
            if price < minimum_consume:
                raise CommonException('不满足最低消费', 1060)
            rebat_price = price - money_equivalent_value
        else:
            rebat_price = price * off_percent / 100

        return rebat_price

    def get_alipay(self):
        # 沙箱环境地址：https://openhome.alipay.com/platform/appDaily.htm?tab=info
        app_id = "2016091100486897"
        # POST请求，用于最后的检测
        notify_url = "http://47.94.172.250:8804/page2/"
        # notify_url = "http://www.wupeiqi.com:8804/page2/"
        # GET请求，用于页面的跳转展示
        return_url = "http://47.94.172.250:8804/page2/"
        # return_url = "http://www.wupeiqi.com:8804/page2/"
        merchant_private_key_path = "utils/keys/app_private_2048.txt"
        alipay_public_key_path = "utils/keys/alipay_public_2048.txt"

        alipay = AliPay(
            appid=app_id,
            app_notify_url=notify_url,
            return_url=return_url,
            app_private_key_path=merchant_private_key_path,
            alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
            debug=True,  # 默认False,
        )
        return alipay
