import sys
import json
import logging
import csv
from models import Company  # , CompanyShareholder, CompanyManager
from urllib.parse import quote
from util.httpclient import Request


sys.path.append('..')

TycQueryApi = "https://api9.tianyancha.com/services/v3/search/sNorV3/{q}"
TycPortraitApi = "https://api9.tianyancha.com/services/v3/t/common/baseinfoV5/{eid}"
TycShareholderPostApi = "https://capi.tianyancha.com/cloud-facade/company/familyBucket"
TycEnterpriseManagerPostApi = "https://capi.tianyancha.com/cloud-facade/company/familyBucket"
TycEnterpriseRiskApi = "https://api9.tianyancha.com/services/v3/risk/companyRiskInfoV4?{id}"

# 天眼查头信息
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "version": "TYC-XCX-WX",
    "Host": "api9.tianyancha.com",
    "Authorization": '0###oo34J0VKzLlpdvf8kgFkMlfU_IPY###1642087379312###22494f3155c2e5a4be76e503837fa439',
    'x-auth-token': "eyJkaXN0aW5jdF9pZCI6IjE3ZDFjNWVhMzZjNGY2LTA5ZjU2NWUwNWViNTZjLTFjMzA2ODUxLTIwNzM2MDAtMTdkMWM1ZWEzNmRiMzYiLCJsaWIiOnsiJGxpYiI6ImpzIiwiJGxpYl9tZXRob2QiOiJjb2RlIiwiJGxpYl92ZXJzaW9uIjoiMS4xNS4yNCJ9LCJwcm9wZXJ0aWVzIjp7IiR0aW1lem9uZV9vZmZzZXQiOi00ODAsIiRzY3JlZW5faGVpZ2h0IjoxMDgwLCIkc2NyZWVuX3dpZHRoIjoxOTIwLCIkbGliIjoianMiLCIkbGliX3ZlcnNpb24iOiIxLjE1LjI0IiwiJGxhdGVzdF90cmFmZmljX3NvdXJjZV90eXBlIjoi6Ieq54S25pCc57Si5rWB6YePIiwiJGxhdGVzdF9zZWFyY2hfa2V5d29yZCI6IuacquWPluWIsOWAvCIsIiRsYXRlc3RfcmVmZXJyZXIiOiJodHRwczovL3d3dy5nb29nbGUuY29tLyIsImN1cnJlbnRfdXJsIjoiaHR0cHM6Ly93d3cudGlhbnlhbmNoYS5jb20vc2VhcmNoP2tleT0lRTYlOUQlQUQlRTUlQjclOUUlRTYlOTklQUUlRTUlODUlQjQlRTQlQkMlODElRTQlQjglOUElRTclQUUlQTElRTclOTAlODYlRTUlOTAlODglRTQlQkMlOTklRTQlQkMlODElRTQlQjglOUEiLCJyZWZlcnJlciI6Imh0dHBzOi8vd3d3LnRpYW55YW5jaGEuY29tL3NlYXJjaD9rZXk9JUU2JTlEJUFEJUU1JUI3JTlFJUU2JTk5JUFFJUU1JTg1JUI0JUU0JUJDJTgxJUU0JUI4JTlBJUU3JUFFJUExJUU3JTkwJTg2JUU1JTkwJTg4JUU0JUJDJTk5JUU0JUJDJTgxJUU0JUI4JTlBIiwidHljaWQiOiI0MmMxZTY1MDQ0ZjYxMWVjYmIxZDY3ZmJiYzEwN2U3NSIsIm5hbWUiOiLmna3lt57mma7lhbTkvIHkuJrnrqHnkIblkIjkvJnkvIHkuJoiLCJtb2R1bGUiOiLkvJjotKjlrp7lkI3orqTor4EiLCIkaXNfZmlyc3RfZGF5IjpmYWxzZX0sImFub255bW91c19pZCI6IjE3ZDFjNWVhMzZjNGY2LTA5ZjU2NWUwNWViNTZjLTFjMzA2ODUxLTIwNzM2MDAtMTdkMWM1ZWEzNmRiMzYiLCJ0eXBlIjoidHJhY2siLCJldmVudCI6InNlYXJjaF9yZXN1bHRfZXhwdXJlIiwiX3RyYWNrX2lkIjo3MjUyNDM3Mjd9"
}


class TycClient:
    def __init__(self, payload=None):
        self.payload = payload
        self.keyword = None
        self.src = []
        self.brand_and_agencies = []
        self.companies = []

    def search(self, keyword: str):
        # 根据关键字搜索相关企业信息
        # :param keyword: 关键字
        # :return:
        self.keyword = keyword
        if not self.payload:
            self.payload = {
                "pageNum": 1,
                "pageSize": 20,
                "sortType": 0
            }
        url = TycQueryApi.format(q=quote(keyword))
        data = Request(url, self.payload, headers=REQUEST_HEADERS).data
        if data:
            api_data = json.loads(data)
            if api_data.get("state") == 'ok':
                self.src = api_data.get("data", {}).get("companyList", [])
                self.brand_and_agencies = api_data.get(
                    "data", {}).get("brandAndAgencyList", [])
                self.__post_process__()
            else:
                logging.info("查询异常：[%s]" % api_data)
        return self

    def __post_process__(self):
        if not self.src:
            return

        company_list = self.src
        for company in company_list:
            company_entity = Company()
            # 公司检索的关键字
            company_entity.keyword = self.keyword
            # 公司主体基本信息
            self.EntityHelper.__basic_info__(company, company_entity)

            def is_equal(b_and_a):
                return company.get('id') == b_and_a.get('graphId')
            try:
                # 公司主体融资阶段、竞品信息
                brand_and_agency = filter(
                    is_equal, self.brand_and_agencies).__next__()
                self.EntityHelper.__another_info__(
                    brand_and_agency, company_entity)
            except Exception as e:
                pass
            # 公司详情
            detail_resp = Request(TycPortraitApi.format(
                eid=company.get("id")), headers=REQUEST_HEADERS).data
            if detail_resp:
                company_portrait = json.loads(detail_resp)
                # 公司详情补充信息
                if company_portrait.get("state") == 'ok':
                    self.EntityHelper.__additional__(
                        company_portrait.get("data", {}), company_entity)

            # 以下功能待修复

            # # 公司股东信息
            # shareholder_request_body = {
            #     "graphId": company.get("id"),
            #     "hkVersion": 1,
            #     "typeList": {
            #         "shareHolder": {
            #             "pageNum": 1,
            #             "pageSize": 20,
            #             "required": "true"
            #         }
            #     }
            # }

            # shareholder_resp = Request(TycShareholderPostApi, method='post',
            #                            json=shareholder_request_body, headers=REQUEST_HEADERS).data
            # if shareholder_resp:
            #     company_shareholder = json.loads(shareholder_resp)
            #     # 公司详情补充信息
            #     if company_shareholder.get("state") == 'ok':
            #         self.EntityHelper.__shareholder__(company_shareholder.get(
            #             "data", {}).get("shareHolder", {}), company_entity)

            # # 公司高管信息
            # manager_request_body = {
            #     "graphId": company.get("id"),
            #     "hkVersion": 1,
            #     "typeList": {
            #         "companyStaff": {
            #             "pageNum": 1,
            #             "pageSize": 20,
            #             "required": "true"
            #         }
            #     }
            # }
            # manager_resp = Request(TycEnterpriseManagerPostApi, method='post',
            #                        json=manager_request_body, headers=REQUEST_HEADERS).data
            # if manager_resp:
            #     company_manager = json.loads(manager_resp)
            #     # 公司详情补充信息
            #     if company_manager.get("state") == 'ok':
            #         self.EntityHelper.__company_manager__(company_manager.get(
            #             "data", {}).get("companyStaff", {}), company_entity)

            # 信息采集完毕，加入列表
            self.companies.append(company_entity)

    def save_to_csv(self, filename: str):
        pass

    class EntityHelper:
        @staticmethod
        def __basic_info__(src: dict, target: Company):
            # 公司外部系统ID
            target.id = src.get('id', '-')
            # 公司名称
            target.name = src.get(
                'name', '-').replace('<em>', '').replace('</em>', '')
            # 公司简称
            target.short_name = src.get('alias', '-')
            # 公司法人
            target.representative = src.get('legalPersonName', '-')
            # 公司成立时间
            target.found_time = src.get('estiblishTime', '-')[0:10]
            # 公司地址
            target.company_address = src.get('regLocation', '-')
            # 公司注册地址
            target.register_address = src.get('regLocation', '-')
            # 公司所在省份，例：浙江，北京，广东
            target.province = src.get('base', '-')
            # 公司所在市
            target.city = src.get('city', '-')
            # 公司所在区
            target.district = src.get('district', '-')
            # 公司经营状态
            target.biz_status = src.get('regStatus', '-')
            # 公司地址经纬度坐标
            target.geoloc = str({
                'latitude': src.get('latitude', '-'),
                'longitude': src.get('longitude', '-')
            })
            # 公司邮箱列表
            target.emails = src.get(
                'emails', ['-']).split(';')[0].replace('\t', '')
            # 公司联系方式列表
            target.phones = src.get('phoneList', [])
            # 公司联系方式
            target.contact = src.get('phoneNum', '-')
            # 公司经营范围
            target.biz_scope = src.get('businessScope', '-')
            # 公司类型
            target.company_type = src.get(
                'companyOrgType', '-').replace('\t', '')
            # 公司质量分数
            target.score = src.get('orginalScore', 0)
            # 公司注册资本
            target.register_capital = src.get('regCapital', '-')
            # 公司统一社会信用代码
            target.credit_code = src.get('creditCode', '-')
            # 公司纳税号
            target.taxpayer_code = src.get('taxCode')
            if not target.taxpayer_code:
                target.taxpayer_code = target.credit_code
            # 公司注册号
            target.register_code = src.get('regNumber', '-')
            # 公司组织机构代码
            target.organization_code = src.get('orgNumber', '-')
            # 公司标签列表
            target.tags = src.get('labelListV2', [])
            # 公司行业分类
            target.industry = src.get('categoryStr', '-')

        @staticmethod
        def __another_info__(brand_and_agency: dict, company: Company):
            # 公司融资轮次
            company.financing_round = brand_and_agency.get("round", "未知")
            # 公司竞品
            company.competitions = brand_and_agency.get("jingpinName", [])
            # 公司logo
            company.logo = brand_and_agency.get("logo")
            # 公司简介
            company.company_desc = brand_and_agency.get("intro")

        @staticmethod
        def __additional__(src: dict, company: Company):
            # 公司英文名
            company.english_name = src.get('property3')
            if not company.english_name:
                company.english_name = src.get('nameEn', '-')
            # 公司注册机构
            company.register_institute = src.get('regInstitute', '-')
            # 公司网站地址集
            company.websites = src.get('websiteList', '-')
            # 公司实缴资本
            company.actual_capital = src.get('actualCapital', '缺省')
            # 公司曾用名
            company.used_name = src.get('historyNames', '-')
            # 公司员工人数
            company.staffs = src.get('socialStaffNum', None)
            if not company.staffs:
                company.staffs = src.get('staffNum', 1)
            # 公司纳税地址
            company.tax_address = src.get('taxAddress', None)
            if not company.tax_address:
                company.tax_address = src.get('regLocation', '-')
            # 公司纳税银行
            company.taxpayer_bank = src.get('taxBankName', '-')
            # 公司涉足领域标签
            company.portraits = src.get('portray', [])
            if not company.logo:
                company.logo = src.get('logo')
            if not company.company_desc:
                company.company_desc = src.get('baseInfo', '-')

        # 以下函数待修复

        # @staticmethod
        # def __shareholder__(src: dict, company: Company):
        #     holder_list = src.get("holderList", [])
        #     for holder in holder_list:
        #         if holder:
        #             shareholder = CompanyShareholder()
        #             shareholder.name = holder.get("name")
        #             shareholder.alias = holder.get("alias")
        #             shareholder.avatar = holder.get("logo")
        #             shareholder.control_ratio = holder.get("proportion")
        #             shareholder.tags = [tag.get("name")
        #                                 for tag in holder.get("tagList", [])]
        #             company.shareholders.append(shareholder)

        # @staticmethod
        # def __company_manager__(src: dict, company: Company):
        #     manager_list = src.get("result", [])
        #     manager_type = src.get("staffTitle", "-")
        #     for manager in manager_list:
        #         company_manager = CompanyManager()
        #         company_manager.manager_type = manager_type
        #         company_manager.name = manager.get("name", "-")
        #         company_manager.titles = manager.get("typeJoin", [])
        #         company.managers.append(company_manager)
