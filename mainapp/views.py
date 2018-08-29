from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# 下载文件要用
from django.http import FileResponse, HttpResponseRedirect
from mainapp import dao as mainapp_dao
from mainapp import recommend as mainapp_RMD
import datetime
import random

print('view')
global RMD
RMD = mainapp_RMD.FoodRMD()


# Create your views here.

# 用户要注册
def register(request):
    # FIXME 完成注册功能
    if request.method == 'POST':
        # 获取用户名和密码
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        # 检查字段缺失
        if username is None or password is None or \
                username == "" or password == "":
            return render(request, r'web/login.html', {'stat': -1})
        # 检查用户名是否已经注册过了
        if mainapp_dao.docCountInUser({"username": username}) > 0:
            return render(request, r'web/login.html', {'stat': -2})
        # 添加账户名和密码
        mainapp_dao.addDocInUser({"username": username, "password": password})
        # 正确状态返回
        return render(request, r'web/login.html', {'stat': 0})
    # 请求形式是非法的
    return render(request, r'web/login.html', {'stat': -3})


# 去登录界面
def getLoginPage(request):
    return render(request, r'web/login.html')


# 用户要去主页(可能是登录操作,也可能就是单纯的页面切换操作)
def getIndexPage(request):
    mylst = [1 for i in range(12)]  # 方便开发用
    # 看看Session里有没有,有就直接进不做校验
    print("从Session里检查")
    if request.session.get('_id') is not None and request.session.get('username') is not None:
        print("Session校验成功")
        favourFood = mainapp_dao.favouriateFood(request.session.get('username'))
        hotFood = mainapp_dao.hotFood()
        return render(request, r'web/index.html', {'favourllst': favourFood,
                                                   'hotlist': hotFood})
    # 如果是登录操作
    elif request.method == 'POST':
        # 获取用户名和密码
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        # 检查字段缺失
        if username is None or password is None or \
                username == "" or password == "":
            return render(request, r'web/login.html', {'stat': -1})
        # FIXME 使用用户名和密码校验身份,并从DB中获取该用户id
        user = mainapp_dao.firstDocInUser({"username": username, "password": password})
        if user is None:
            # 登录失败
            return render(request, r'web/login.html', {'stat': -4})
        # 登录成功,将登录身份存进session里
        request.session['_id'] = user.get('_id').__str__()  # 转成str
        request.session['username'] = user.get('username')
        print("存进了Session里")
        return render(request, r'web/index.html', {'mylst': mylst})
    else:
        # 请先登录!
        return render(request, r'web/login.html', {'stat': -5})


# 用户要注销登录
def logOut(request):
    request.session.flush()  # 键和值一起清空
    return render(request, r'web/login.html')


# 用户要进入账户资料页面
def getCntMsg(request):
    return render(request, r'web/cntmsg.html')


# 用户要进入身体信息页面
def getBdyMsg(request):
    return render(request, r'web/bdymsg.html')


# 用户要进入昨日打卡页面
def getPunchPage(request):
    # 获取服务器时间
    serverDate = datetime.datetime.now().strftime('%Y-%m-%d')
    print(request.session)
    '''
    mylst = [1 for i in range(12)]  # 方便开发用
    print("从Session里检查")
    if request.session.get('_id') is not None and request.session.get('username') is not None:
        print("Session校验成功")
        return render(request, r'web/index.html', {'mylst': mylst})
    # 如果是登录操作
    elif request.method == 'POST':
        # 获取用户名和密码
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        # 检查字段缺失
        if username is None or password is None or \
                username == "" or password == "":
            return render(request, r'web/login.html', {'stat': -1})
        # FIXME 使用用户名和密码校验身份,并从DB中获取该用户id
        user = mainapp_dao.firstDocInUser({"username": username, "password": password})
        if user is None:
            # 登录失败
            return render(request, r'web/login.html', {'stat': -4})
        # 登录成功,将登录身份存进session里
        request.session['_id'] = user.get('_id').__str__()  # 转成str
        request.session['username'] = user.get('username')
        print("存进了Session里")
        return render(request, r'web/index.html', {'mylst': mylst})
    else:
        # 请先登录!
        return render(request, r'web/login.html', {'stat': -5})
    '''

    return render(request, r'web/punch.html', {'serverDate': serverDate})


# 用户要进入一日三餐建议页面
def getMealsPage(request):
    username = request.session.get('username')
    recommend = RMD.Single_Recommand(username, 30)
    breakfast, RecommendList, sneak = mainapp_dao.OneDayRecommend(recommend)
    lunch = RecommendList[0]
    dinner = RecommendList[1]
    return render(request, r'web/meals.html',
                  {'breakfast': breakfast,
                   'lunch': lunch,
                   'dinner': dinner,
                   'sneak': sneak})


# 用户要进入设置页面
def getSettingPage(request):
    return render(request, r'web/setting.html')


# 用户要进入反馈页面
def getPropPage(request):
    return render(request, r'web/prop.html')


# 用户要进入食物推荐页面
def getRecommendPage(request, page='1'):
    username = request.session.get('username')
    print(username)
    recommend = RMD.Single_Recommand(username, 70)
    if len(set(recommend))<70:
        recommend=recommend[0:len(set(recommend))]
        recommend.extend(mainapp_dao.FoodNotEnough(70-len(set(recommend))))
    #    print(recommend)
    RecommendList = random.sample(mainapp_dao.RecommendList(recommend)[12 * (int(page) - 1):12 * (int(page))],12)
    return render(request, r'web/recommend.html',
                  {'mylst': RecommendList,
                   'pglst': [i + 1 for i in range(5)],
                   'page': int(page)})


# 用户要进入饮食计划页面
def getPlanPage(request):
    return render(request, r'web/plan.html')


# 测试下载报表文件
def testDown(request):
    file = open(r'test/测试报表文件.txt', 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="mybb.txt"'
    return response


# 用户要进入某个具体的餐馆页面
def getEateryById(request, id):
    print("获得了餐馆的id", id)
    return render(request, r'web/detail/eatery.html')


# 通过跳转界面添加用户评价
def addEval(request, id):
    print("获得了餐馆的id", id)
    username = request.session.get('username')
    RMD.AddEval(username, mainapp_dao.ID2ShopName(id))
    RMD.AfferADD(username, mainapp_dao.ID2ShopName(id))
    return HttpResponseRedirect(mainapp_dao.ID2Pic(id))
