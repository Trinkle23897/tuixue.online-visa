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
            filterDesc: "Choose Embassy/Consulate",
            filterSystemDesc: "Filter by system: ",
            filterDefault: "Reset to default",
            filterDomestic: "Domestic only",
            filterOverviewOpen: "Show Charts",
            filterOverviewClose: "Collapse Charts",
            at: "at",
            all: "All",
            overviewTitle: "Visa Status Overview",
            overviewEarliest: "Earliest availabe appointment date of today",
            overviewNewest: "Latest fetching result of available appointment date",
            overviewLatest: "Latest available appointment date of today",
            overviewEmailIcon: "Subscribe from email",
            overviewQQIcon: "Subscribe from QQ group / Telegram channel",
            overviewAddtionalIcon: "Additional information",
            overviewEarliestDate: "Earliest Date",
            overviewLatestDate: "Latest Date",
            overviewNewestFetch: "Newest Fetch",
            overviewActions: "Actions",
            notificationInitTitle: "Auto-notification is enabled",
            notificationInitContent: "If a new position pops up, the browser will pop up a notification ASAP",
            notificationTitle: "{{visaTypeDetail}} Visa Status Changed",
            notificationContent: "{{embassyName}} changed from {{prevAvaiDate}} to {{currAvaiDate}}.",
            notificationBlocked: "Notifications blocked. Please enable it in your browser.",
            notificationNoSupport: "This browser does not support web notification.",
            QQTGModalTitle: "QQ Group and Telegram Channel Subscription for F1 Visa",
            QQTGModalContentTG: "Telegram Channel link: ",
            QQTGModalContentQQDesc:
                "QQ group entry password is the site URL, a total of 13 characters t***e. All groups' content are the same.",
            QQTGModalContentQQ: "QQ group #{{index}}: ",
        },
    },
    zh: {
        translation: {
            countryCode: "{{countryName, country}}",
            visaStatus: "签证预约状态",
            webNotify: "网页自动通知",
            sysStatus: "系统当前状态",
            checkee: "签证结果统计",
            filterDesc: "选择使馆/领事馆",
            filterSystemDesc: "选择系统：",
            filterDefault: "恢复默认",
            filterDomestic: "只看国内",
            filterOverviewOpen: "展开图表",
            filterOverviewClose: "收起图表",
            at: "于",
            all: "全部",
            Location: "地点",
            overviewTitle: "美国签证预约时间",
            overviewEarliest: "今天出现的最早可预约日期",
            overviewNewest: "当前日期",
            overviewLatest: "今天出现的最晚可预约日期",
            overviewEmailIcon: "邮件订阅",
            overviewQQIcon: "QQ群/Telegram频道订阅",
            overviewAddtionalIcon: "更多信息",
            overviewEarliestDate: "最早日期",
            overviewLatestDate: "最晚日期",
            overviewNewestFetch: "当前日期",
            overviewActions: "操作",
            notificationInitTitle: "已开启自动通知功能",
            notificationInitContent: "如果有新位置放出来，浏览器会第一时间弹出通知",
            notificationTitle: "{{visaTypeDetail}} 签证放新位置了",
            notificationContent: "{{embassyName}}: {{prevAvaiDate}} -> {{currAvaiDate}}",
            notificationBlocked: "通知被浏览器屏蔽了，请手动打开它",
            notificationNoSupport: "这个浏览器不支持网页版通知",
            QQTGModalTitle: "QQ群/Telegram频道订阅F签信息",
            QQTGModalContentTG: "Telegram频道链接：",
            QQTGModalContentQQDesc: "QQ群入群密码是本站网址，共13个字符t***e，所有群内容一致",
            QQTGModalContentQQ: "QQ群{{index}}群：",
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