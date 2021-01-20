import i18n from "i18next";
import countries from "i18n-iso-countries";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

// register languages for browser versions
countries.registerLocale(require("i18n-iso-countries/langs/en.json"));
countries.registerLocale(require("i18n-iso-countries/langs/zh.json"));

export { countries };

const resources = {
    en: {
        translation: {
            countryCode: "{{countryName, country}}",
            visaStatus: "Visa Status",
            webNotify: "Auto Web Notify",
            sysStatus: "System Status",
            checkee: "Check Reporter",
            filter: {
                desc: "Choose Embassy/Consulate",
                systemDesc: "Filter by system: ",
                default: "Reset to default",
                domestic: "Domestic only",
                placeholder: "Search or select U.S. Embassy or Consulate",
            },
            overMinuteChartTitle: "First available appointment change within 24h",
            overDateChartTitle: "Appointment change within 60 days - {{embassyName}}",
            overDateChartSubtitle:
                ", appointments should be made {{earliestDiffMean}} ~ {{latestDiffMean}} days in advance",
            overDateChartSubtitleNull: ", without any available appointment",
            at: "at",
            all: "All",
            refreshDone: "Done with refresh",
            overview: {
                title: "Visa Status Overview",
                earliest: "Earliest availabe appointment date of today",
                newest: "Latest fetching result of available appointment date",
                latest: "Latest available appointment date of today",
                emailIcon: "Subscribe from email",
                QQIcon: "Subscribe from QQ group / Telegram channel",
                addtionalIcon: "Additional information",
                earliestDate: "Earliest Date",
                latestDate: "Latest Date",
                newestFetch: "Newest Fetch",
                actions: "Actions",
                aheadDay: "Date Ahead",
                ahead: "Average appointment date in advance",
            },
            notification: {
                initTitle: "Auto-notification is enabled",
                initContent: "If a new position pops up, the browser will pop up a notification ASAP",
                title: "{{visaTypeDetail}} Visa Status Changed",
                content: "{{embassyName}} changed from {{prevAvaiDate}} to {{currAvaiDate}}.",
                blocked: "Notifications blocked. Please enable it in your browser.",
                noSupport: "This browser does not support web notification.",
            },
            TGDomestic: "Telegram Channel link (domestic): ",
            TGNonDomestic: "Telegram Channel link (global): ",
            QQDescDomestic:
                "QQ group entry password is the site URL, a total of 13 characters t***e. All groups' content are the same.",
            QQDescNonDomestic:
                "The global version includes popular areas for getting visa in third country, including {{cities}}",
            QQGroupDomestic: "Domestic #{{index}}: ",
            QQGroupNonDomestic: "Global #{{index}}: ",
            additionalInfoTop: {
                part1: "Just go up and click on the icon (",
                part2: ") next to the chart.",
            },
            footer: {
                prjDesc: [
                    "Features: Auto-notification at webpage (no need to keep an eye on it), customize the location filter that only you concerned about, update data in real-time, new QQ groups with 3rd countries (Ecuador, Singapore, UK) and add the corresponding issues going there",
                    "Project Info: [GitHub Page](https://github.com/Trinkle23897/tuixue.online-visa); Author list: [Trinkle23897](https://github.com/Trinkle23897/), [z3dd1cu5](https://github.com/z3dd1cu5), [BenjiTheC](https://github.com/BenjiTheC)",
                    "If you think tuixue.online is helpful, please donate for our website, we appreciate your support!",
                ].join("\n\n"),
                part1: "This website has witnessed a total of ",
                part2: " tuixue (withdrawals). ",
                part3: "About the poor author",
            },
            disqus: {
                domestic: "Disqus (Domestic version)",
                global: "Disqus (Global version)",
                loadFail: "Unable to load Disqus comments :(",
            },
            emailForm: {
                title: "Email Subscription",
                selectVisaType: "Select Visa Type",
                selectEmbassy: "Select Embassy",
                selectTill: "Select Date of Till",
                emailAddress: "Email Address",
                requireVisaType: "Visa Type field is required!",
                requireEmbassy: "Embassy field is required!",
                requireEmail: "Email address is required!",
                removeItem: "Remove this item",
                addSubsItem: "Add another Subscription Rule",
                subscribe: "Submit",
                unsubscribe: "Submit",
                tab: {
                    subscription: "Subscription",
                    unsubscription: "Unsubscription",
                },
                successText: {
                    confirming: "Subscription request sent. Please check your email.",
                    subscribed: "Successfully subscribed. Thank you!",
                    deleted: "Successfully unsubscribed. Thank you!",
                },
                loadingText: "We are processing your request.",
                failureText: "Something goes wrong, we are sorry. Please try again.",
                redirecting: "Redirecting to home page in 3 seconds...",
                closing: "Closing in 3 seconds...",
                description: [
                    "## Email Subscription",
                    "Whenever the first available appointment becomes earlier, tuixue.online will send you an email notification. The actual delay is about 10s.",
                    "- Submit (or update) your email subscription: fill in the form and submit, then a confirmation email will be sent from dean@tuixue.online. **Please click on the confirmation link to make your subscription active**.",
                    "- Effect: if one subscribes to Beijing F1 visa with a date of X (left blank for FOREVER), he/she will receive an email notification when this place releases any available appointment slot earlier than (or including) date X.",
                    '- Unsubscribe: click "Unsubscription" tab below, enter the email, and a confirmation letter will be sent to your email address, click the corresponding link inside.',
                    "- Pattern: CGI system will release the quota released by others 6-8 hours ago at XX:48, AIS system is released every 5 minutes (00/05/.../55) for the quota returned by others 5-7 hours ago; if the notification email received doesn't conform to this pattern, most likely a large quota has been released.",
                ].join("\n\n"),
            },
        },
    },
    zh: {
        translation: {
            countryCode: "{{countryName, country}}",
            visaStatus: "签证预约状态",
            webNotify: "网页自动通知",
            sysStatus: "系统当前状态",
            checkee: "签证结果统计",
            filter: {
                desc: "选择使领馆",
                systemDesc: "选择系统：",
                default: "恢复默认",
                domestic: "只看国内",
                placeholder: "搜选使领馆",
            },
            overMinuteChartTitle: "24h内可预约日期变动情况",
            overDateChartTitle: "{{embassyName}}60天内预约日期变动情况",
            overDateChartSubtitle: "，平均需要提前{{earliestDiffMean}}到{{latestDiffMean}}天预约",
            overDateChartSubtitleNull: "，没有任何预约名额",
            at: "于",
            all: "全部",
            Refresh: "刷新数据",
            refreshDone: "已刷新至最新数据",
            Location: "地点",
            overview: {
                title: "美国签证预约时间",
                earliest: "今天出现的最早可预约日期",
                newest: "当前日期",
                latest: "今天出现的最晚可预约日期",
                emailIcon: "个性化邮件订阅",
                QQIcon: "QQ群/Telegram频道订阅",
                addtionalIcon: "更多信息",
                earliestDate: "最早日期",
                latestDate: "最晚日期",
                newestFetch: "当前日期",
                actions: "操作",
                aheadDay: "提前天数",
                ahead: "平均需要提前预约天数",
            },
            notification: {
                initTitle: "已开启自动通知功能",
                initContent: "如果有新位置放出来，浏览器会第一时间弹出通知",
                title: "{{visaTypeDetail}} 签证放新位置了",
                content: "{{embassyName}}: {{prevAvaiDate}} -> {{currAvaiDate}}",
                blocked: "通知被浏览器屏蔽了，请手动打开它",
                noSupport: "这个浏览器不支持网页版通知",
            },
            TGDomestic: "Telegram 频道（国内版）链接：",
            TGNonDomestic: "Telegram 频道（国际版）链接：",
            QQDescDomestic: "QQ群入群密码是本站网址，共13个字符t***e，所有群内容一致",
            QQDescNonDomestic: "国际版仅包含目前第三国签证热门地区，包括：{{cities}}",
            QQTGModalContentQQ: "QQ群{{index}}群：",
            QQGroupDomestic: "国内{{index}}群：",
            QQGroupNonDomestic: "国际{{index}}群：",
            additionalInfoTop: {
                part1: "最上方点击图表旁边的图标（",
                part2: "）即可",
            },
            footer: {
                prjDesc: [
                    "功能概览：网页版能够穿透通知（不用一直盯着或者手动刷了），可以只选自己关注的城市（不用像现在这样一次刷这么多），数据实时更新，新加了国外的qq群和去往对应第三国各种注意事项（厄瓜多尔、新加坡、英国）",
                    "项目信息：[GitHub项目地址](https://github.com/Trinkle23897/tuixue.online-visa)、[作者GitHub](https://github.com/Trinkle23897/)、改进版爬虫作者 [z3dd1cu5](https://github.com/z3dd1cu5)、新版网站贡献者 [BenjiTheC](https://github.com/BenjiTheC)",
                    "写这玩意还是花了一些时间的，维护也不容易（服务器要钱，验证码要钱，邮件系统是私搭的可能会被封），随喜打赏",
                ].join("\n\n"),
                part1: "本网站一共见证了",
                part2: "人次的失学。",
                part3: "关于可怜的差点被全聚德的作者",
            },
            disqus: {
                domestic: "原国内版评论区",
                global: "原国际版评论区",
                loadFail: "Disqus评论区无法加载 :(",
            },
            emailForm: {
                title: "个性化邮件订阅",
                selectVisaType: "选择签证类型",
                selectEmbassy: "选择使领馆",
                selectTill: "截止日期（空为永久）",
                emailAddress: "邮箱地址",
                requireVisaType: "签证类型不能为空",
                requireEmbassy: "使领馆不能为空",
                requireEmail: "邮箱不能为空",
                removeItem: "删除该条规则",
                addSubsItem: "添加另一条订阅规则",
                subscribe: "点击订阅",
                unsubscribe: "取消订阅",
                tab: {
                    subscription: "增加订阅",
                    unsubscription: "取消订阅",
                },
                successText: {
                    confirming: "已收到订阅请求，请检查确认邮件",
                    subscribed: "已成功订阅",
                    deleted: "已成功取消订阅",
                },
                loadingText: "正在处理中",
                failureText: "不知道出啥问题了，可能需要再试试或者报bug？",
                redirecting: "3秒后前往主页...",
                closing: "3秒后关闭...",
                description: [
                    "## 个性化邮件订阅",
                    "每当时间变前的时候，tuixue.online就会向您发送邮件通知。最好使用国内邮箱比如qq（因为可以绑定微信，能第一时间看到），实测延时大概10s",
                    "- 提交（或更新）订阅：填写之后点击提交，dean@tuixue.online会发送确认邮件，**请点击里面的确认链接使订阅生效**；",
                    "- 效果：比如订阅了北京F签信息，截止日期为X（留空为永久），如果当地出现了早于（或包含）X日期的可预约时间，则会收到一封邮件通知；",
                    '- 取消订阅：点击下方"取消订阅"标签页，输入邮箱，一封取消订阅确认信会发送至邮箱中，点击里面对应链接即可；',
                    "- 规律：CGI系统会在每小时48分的时候放出6-8小时前别人放出的名额，AIS系统是每隔5分钟（00/05/…/55）放出别人5-7小时前别人退掉的名额；如果收到的通知邮件不符合这个时间规律的话，多半是放出来了一大波名额。",
                ].join("\n\n"),
            },
        },
    },
};

i18n.use(LanguageDetector)
    .use(initReactI18next)
    .init({
        resources,
        fallbacklng: "zh",
        interpolation: {
            escapeValue: false,
            format: (value, format, lng) =>
                format === "country" ? countries.getName(value, lng, { select: "official" }) : value,
        },
    });

export const namespace = "translation";
export const lngs = { en: "en", zh: "zh" };
export default i18n;
