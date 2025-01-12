from functools import partial

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.utils import timezone
from django.utils import translation
from django.db import transaction
from django.http import Http404
from django.db.models import Q
from django.core.cache import cache
from django.contrib import messages
from django.utils.translation import gettext as _
from django.template import loader
import icalendar

import util.ctrl
import util.time
import util.user
import util.userexp
from main.models import User, Progress, Chat
import KyanToolKit
ktk = KyanToolKit.KyanToolKit()


@util.user.login_required
def list(request):
    """进度列表：显示所有进行中、待开始、追剧中的进度"""
    user = util.user.getCurrentUser(request)
    # get user's progresses
    progresses = Progress.objects.filter(userid=user.id).order_by('-modified')
    prg_list = {}
    if len(progresses):
        for st, stzh in Progress.STATUSES.get('active'):
            prg_list[st] = progresses.filter(status=st)
        prg_list["inprogress_and_follow"] = progresses.filter(Q(status='inprogress') | Q(status='follow'))
    else:
        TITLE = _("欢迎使用") + " 「" + _("我的进度") + "」"
        if not user.getChats('received').filter(senderid=Chat.objects.getSyschatUser().id, title=TITLE).exists():
            chat_content = loader.render_to_string("progress/msg-welcome.html", {'title': TITLE})
            Chat.objects.sendBySys(user, title=TITLE, content=chat_content)
    # add exps
    util.userexp.addExp(user, "progress", 1, _("访问「{}」页面").format(_("进度列表")))
    # render
    context = {
        "prglist": prg_list,
    }
    return render(request, "progress/list.html", context)


@util.user.login_required
def archive(request):
    """进度存档：显示所有已完成、已冻结的进度"""
    user = util.user.getCurrentUser(request)
    # get user's progresses
    progresses = Progress.objects.filter(userid=user.id).order_by('-modified')
    prg_list = {}
    if len(progresses):
        for st, stzh in Progress.STATUSES.get('archive'):
            prg_list[st] = progresses.filter(status=st)
    # add exps
    util.userexp.addExp(user, 'progress', 1, _("访问「{}」页面").format(_("进度存档")))
    # render
    context = {
        'prglist': prg_list,
    }
    return render(request, 'progress/archive.html', context)


@util.user.login_required
def search(request):
    """进度搜索：筛选所有进度"""
    context = {}
    # get user
    user = util.user.getCurrentUser(request)
    # get user's progresses
    progresses = Progress.objects.filter(userid=user.id).order_by('created')
    context['prglist'] = progresses
    # pass searched keyword
    keyword = request.GET.get('kw') or ""
    # add exps
    util.userexp.addExp(user, 'progress', 1, _("访问「{}」页面").format(_("进度搜索")))
    # render
    context = {
        'prglist': progresses,
        'keyword': keyword,
    }
    return render(request, 'progress/search.html', context)


@util.user.login_required
def timeline(request):
    """进度历程：显示所有进度的时间轴"""
    context = {}
    # get user
    user = util.user.getCurrentUser(request)
    # get user's progresses
    progresses = Progress.objects.filter(userid=user.id).order_by('-modified')
    year_earliest = Progress.objects.filter(userid=user.id).earliest('created').created.year
    year_latest = Progress.objects.filter(userid=user.id).latest('modified').modified.year
    # add timeline info
    context['prglist_by_year'] = []
    for year in range(year_earliest, year_latest + 1):
        context['prglist_by_year'].append([year, progresses.filter(Q(created__year=year) | Q(modified__year=year))])
    context['prglist'] = progresses
    # add exps
    util.userexp.addExp(user, 'progress', 1, _("访问「{}」页面").format(_("进度列表")))
    # render
    return render(request, 'progress/timeline.html', context)


@util.user.login_required
def detail(request):
    """进度详情页"""
    errMsg = partial(util.ctrl.infoMsg, title=_('错误'))
    # get inputs
    user = util.user.getCurrentUser(request)
    progressid = request.GET.get('id')
    if not progressid:
        raise Http404(_("{} 参数不能为空").format("Progress ID"))
    # get progress
    progress = Progress.objects.get_or_404(id=progressid)
    # check owner
    if progress.userid != user.id:
        return errMsg(_("这个进度不属于您，因此您不能{}该进度").format(_("查看")), url='/progress/list')
    # add exp
    util.userexp.addExp(user, "progress", 1, _("查看进度《{}》的详情").format(progress.name))
    # calcs
    aux = {
        "time": {},
        "esti": {},
    }
    aux["time"]["c2n"] = util.time.formatDateToNow(progress.created, "largest")
    aux["time"]["m2n"] = util.time.formatDateToNow(progress.modified, "largest")
    aux["time"]["c2m"] = util.time.formatTimedelta(progress.getTimedelta("c2m"))
    if progress.total and progress.current:  # 非追剧中、非待开始有预计完成时间.
        esti_finish_timedelta = progress.getTimedelta("c2n") / progress.current * (progress.total - progress.current)
        esti_finish_date = progress.modified + esti_finish_timedelta
        aux["esti"]["finish_date"] = esti_finish_date
        aux["esti"]["finish_time"] = util.time.formatDateToNow(esti_finish_date, "largest")
    if progress.current:  # 平均阅读速度.
        speed = progress.getTimedelta("speed")
        if speed:
            aux["time"]["speed"] = util.time.formatTimedelta(speed)
    # render
    context = {}
    context["prg"] = progress
    context["aux"] = aux
    return render(request, "progress/detail.html", context)


def imagecolor(request):  # AJAX #PUBLIC
    """异步获取一个url的颜色"""
    url = request.GET.get('url')
    progressid = request.GET.get('progressid')
    result = {}
    if progressid:  # has-progressid
        cache_key = 'progress:{}:covercolor'.format(progressid)
        cache_timeout = 60 * 60 * 24 * 7 * 2  # 2 weeks
        cached_color = cache.get(cache_key)
        if cached_color:  # has-progressid & cached
            result['is_cached'] = True
            result['color'] = cached_color
            return util.ctrl.returnJson(result)
        else:  # has-progressid & not-cached
            result['is_cached'] = False
    if url:  # no-progressid or not-cached
        try:
            color = ktk.imageToColor(url, mode='hex')
        except Exception as e:
            return util.ctrl.returnJsonError(str(e))
        result['color'] = color
        if progressid:
            cache.set(cache_key, color, cache_timeout)
    return util.ctrl.returnJson(result)


@util.user.login_required
def update(request):  # POST
    """detail页面，编辑模式的保存"""
    ERROR_TITLE = _("更新失败")
    errMsg = partial(util.ctrl.infoMsg, title=ERROR_TITLE)
    # get inputs
    progressid = request.POST.get('id')
    if not progressid:
        raise Http404(_("{} 参数不能为空").format("Progress ID"), title=ERROR_TITLE)
    name = request.POST.get('name')
    comment = request.POST.get('comment')
    weblink = request.POST.get('weblink')
    total = request.POST.get('total')
    total = int(total) if total else 0
    current = request.POST.get('current')
    current = int(current)
    keep_modified = request.POST.get("keepmodified") or None
    save_to_detail = request.POST.get('savetodetail') or None
    if not name:
        return errMsg(_("名称不能为空"))
    if not weblink:
        weblink = ""
    if current <= 0:
        current = 0
    if total > 0 and current > total:
        return errMsg(_("初始进度 {c} 不能大于总页数 {t}").format(c=current, t=total))
    # get progress
    progress = Progress.objects.get_or_404(id=progressid)
    # check owner
    user = util.user.getCurrentUser(request)
    if progress.userid != user.id:
        return errMsg(_("这个进度不属于您，因此您不能{}该进度").format(_("更新")))
    # add exp
    util.userexp.addExp(user, "progress", 5, _("编辑进度《{}》成功").format(progress.name))
    # save
    progress.current = current
    progress.name = name
    progress.comment = comment
    progress.weblink = weblink
    progress.total = total
    progress.save(keep_modified=keep_modified)
    # render
    messages.success(request, _("进度") + " 《{}》 ".format(progress.name) + _("已更新"))
    if save_to_detail:
        redirect_to = "/progress/detail?id={}".format(progress.id)
    else:
        redirect_to = "/progress/list"
    return redirect(redirect_to)


@util.user.login_required
def delete(request):  # POST
    """detail 界面点击删除按钮"""
    errMsg = partial(util.ctrl.infoMsg, title=_("删除失败"))
    # get inputs
    progressid = request.POST.get('id')
    if not progressid:
        raise Http404(_("{} 参数不能为空").format("Progress ID"))
    # get progress
    progress = Progress.objects.get_or_404(id=progressid)
    # check owner
    user = util.user.getCurrentUser(request)
    if progress.userid != user.id:
        return errMsg(_("这个进度不属于您，因此您不能{}该进度").format(_("删除")))
    # save
    progress.delete()
    # add exp
    util.userexp.addExp(user, "progress", 5, _("删除进度《{}》").format(progress.name))
    # render
    messages.success(request, _("进度") + " 《{}》 ".format(progress.name) + _("已删除"))
    return redirect("/progress/list")


@util.user.login_required
def plusone(request):  # GET
    """list 界面点击 +1 按钮"""
    errMsg = partial(util.ctrl.infoMsg, title=_("删除失败"))
    # get inputs
    next_ = request.META.get('HTTP_REFERER') or "/"
    progressid = request.GET.get('id')
    if not progressid:
        raise Http404(_("{} 参数不能为空").format("Progress ID"))
    # get progress
    progress = Progress.objects.get_or_404(id=progressid)
    # check owner
    user = util.user.getCurrentUser(request)
    if progress.userid != user.id:
        return errMsg(_("这个进度不属于您，因此您不能{}该进度").format("+1"))
    # check total
    if progress.total > 0 and progress.current == progress.total:
        return errMsg(_("进度已达到最大值"))
    # save
    progress.current = progress.current + 1
    progress.save()
    messages.success(request, _("进度") + " 《{}》 ".format(progress.name) + "+1 " + _("已更新"))
    # add exp
    util.userexp.addExp(user, "progress", 5, "{i18n_progress} 《{progress.name}》 +1".format(i18n_progress=_("进度"), progress=progress))
    # render
    errMsg = partial(util.ctrl.infoMsg, title=_("+1 失败"))
    return redirect(next_)


@util.user.login_required
def deactivate(request):  # POST
    """detail 界面点击冻结按钮"""
    errMsg = partial(util.ctrl.infoMsg, title=_("错误"))
    # get inputs
    progressid = request.POST.get('id')
    if not progressid:
        raise Http404(_("{} 参数不能为空").format("Progress ID"))
    # get progress
    progress = Progress.objects.get_or_404(id=progressid)
    # check owner
    user = util.user.getCurrentUser(request)
    if progress.userid != user.id:
        return errMsg(_("这个进度不属于您，因此您不能{}该进度").format(_("冻结")))
    # save
    progress.status = 'deactivated'
    progress.save()
    # add exp
    util.userexp.addExp(user, "progress", 5, _("冻结进度《{}》").format(progress.name))
    # render
    messages.success(request, _("进度") + " 《{}》 ".format(progress.name) + _("已冻结"))
    return redirect("/progress/detail?id=" + str(progress.id))


@util.user.login_required
def reactivate(request):
    """detail 界面点击激活进度按钮"""
    errMsg = partial(util.ctrl.infoMsg, title=_("激活失败"))
    # get inputs
    progressid = request.POST.get('id')
    if not progressid:
        raise Http404(_("{} 参数不能为空").format("Progress ID"))
    # get progress
    progress = Progress.objects.get_or_404(id=progressid)
    # check owner
    user = util.user.getCurrentUser(request)
    if progress.userid != user.id:
        return errMsg(_("这个进度不属于您，因此您不能{}该进度").format(_("激活")))
    # save
    progress.resetStatus()
    progress.save()
    # add exp
    util.userexp.addExp(user, "progress", 5, _("恢复已冻结的进度《{}》").format(progress.name))
    # render
    messages.success(request, _("进度") + " 《{}》 ".format(progress.name) + _("已激活"))
    return redirect("/progress/detail?id=" + str(progress.id))


@util.user.login_required
def new(request):
    """list/detail 界面点击新增按钮"""
    # get inputs
    name = request.GET.get("name") or ""
    total = request.GET.get("total") or ""
    weblink = request.GET.get("weblink") or ""
    # load used comments
    user = util.user.getCurrentUser(request)
    progresses = Progress.objects.filter(userid=user.id)
    comment_tags = Progress.objects.getCommentTags(progresses)
    # add exp
    user = util.user.getCurrentUser(request)
    util.userexp.addExp(user, "progress", 2, _("尝试新增进度"))
    # render
    context = {
        "name": name,
        "total": total,
        "weblink": weblink,
        "commenttags": comment_tags,
    }
    return render(request, "progress/new.html", context)


@util.user.login_required
def add(request):
    """新增界面点击保存按钮"""
    errMsg = partial(util.ctrl.infoMsg, title=_("新增失败"))
    # get inputs
    name = request.POST.get("name")
    comment = request.POST.get("comment")
    weblink = request.POST.get("weblink")
    if not weblink:
        weblink = ""
    total = request.POST.get("total")
    total = int(total) if total else 0
    current = request.POST.get("current")
    current = int(current)
    if not name:
        return errMsg(_("名称不能为空"))
    # validate
    if current <= 0:
        current = 0
    if total > 0 and current > total:
        return errMsg(_("初始进度 {c} 不能大于总页数 {t}").format(c=current, t=total))
    # add exp
    user = util.user.getCurrentUser(request)
    util.userexp.addExp(user, "progress", 10, _("新增进度《{}》成功").format(name))
    # save
    progress = Progress(name=name, comment=comment, total=total, current=current, userid=user.id, weblink=weblink)
    progress.save()
    # render
    return redirect("/progress/detail?id={progress.id}".format(progress=progress))


@util.user.login_required
def setsettings(request):  # POST
    """用户设置进度设置的界面"""
    def form_input_to_setting(input_name: str, permission_name: str):
        user = util.user.getCurrentUser(request)
        input_value = request.POST.get(input_name) or "off"
        if input_value == "unset":
            user.delUserpermission(permission_name)
        else:
            user.setUserpermission(permission_name, (input_value == "on"))

    form_input_to_setting("publicical", "progress.public_ical")
    form_input_to_setting("savetodetail", "progress.save_to_detail")
    form_input_to_setting("serviceworker", "progress.service_worker")
    return redirect("/user/setting")


def ical(request):  # GET
    """生成 ical 字符串加入 google calendar"""
    def generate_summery(status, name):
        if status == 'done':
            pattern = "{act} {nm}"
            params = {
                "act": _("完成了"),
            }
        elif status == 'deactivated':
            pattern = "{act} {nm}"
            params = {
                "act": _("冻结了"),
            }
        elif status == 'inprogress':
            pattern = "{nm} {act} {crrt}/{ttl}"
            params = {
                "act": _("进行至"),
                "crrt": prg.current,
                "ttl": prg.total,
            }
        elif status == 'follow':
            pattern = "{nm} {act} {di} {num} {ji}"
            params = {
                "act": _("追剧至"),
                "di": _("第"),
                "num": prg.current,
                "ji": _("集"),
            }
        elif status == 'todo':
            pattern = "{nm} {act} {todo}"
            params = {
                "act": _("加入至"),
                "todo": _("待阅读"),
            }
        else:
            pattern = "{nm} {act}"
            params = {
                "act": _("出错"),
            }
        return pattern.format(nm=name, **params)

    userid = request.GET.get("userid")
    privatekey = request.GET.get("private") or None
    user = User.objects.get_or_404(id=userid)
    if privatekey:  # private mode
        if privatekey != user.privatekey:
            raise Http404(_("获取日历失败") + _("：") + _("用户的私钥不合法"))
    else:  # public mode
        if not user.getUserpermission("progress.public_ical"):
            raise Http404(_("获取日历失败") + _("：") + _("此用户尚未公开其进度日历"))
    # get user's progresses
    progresses = Progress.objects.filter(userid=user.id).order_by('-modified')
    # construct iCalendar
    cal = icalendar.Calendar()
    cal.update({
        "PRODID": "-//kyan001.com//Progress Calendar//{}".format(translation.get_language().upper()),
        "VERSION": "2.0",
        "METHOD": "PUBLISH",
        "CALSACLE": "GREGORIAN",
        "X-WR-CALNAME": "「{t}」@{u}".format(t=_("进度日历"), u=user.nickname),
        "X-WR-TIMEZONE": timezone.get_current_timezone(),
        "X-WR-CALDESC": "http://www.kyan001.com/progress/list",
    })
    for prg in progresses:
        prg_url = "http://www.kyan001.com/progress/detail?id={}".format(prg.id)
        PRGNAME = "《{}》".format(prg.name)
        # create event create
        evnt_crt = icalendar.Event({
            "UID": 'prg:id:{}:create'.format(prg.id),
            "DESCRIPTION": prg_url,
            "URL": prg_url,
            "DTSTART": icalendar.vDatetime(prg.created),
            "DTSTAMP": icalendar.vDatetime(prg.created),
            "SUMMARY": "{act} {nm}".format(act=_("开始看"), nm=PRGNAME),
        })
        cal.add_component(evnt_crt)
        # create event modify
        evnt_mdf = icalendar.Event({
            "UID": 'prg:id:{id}:{st}'.format(id=prg.id, st=prg.status),
            "DESCRIPTION": prg_url,
            "URL": prg_url,
            "DTSTART": icalendar.vDatetime(prg.modified),
            "DTSTAMP": icalendar.vDatetime(prg.modified),
            "SUMMARY": generate_summery(prg.status, PRGNAME),
        })
        cal.add_component(evnt_mdf)
    # render
    return HttpResponse(cal.to_ical(), content_type='text/calendar')
