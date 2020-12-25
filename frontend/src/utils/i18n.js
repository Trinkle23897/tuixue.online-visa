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
            sysStatus: "System Status",
            checkee: "Check Reporter",
            filterDesc: "Add embassies/consulates of your choice",
            filterSystemDesc: "Filter by system: ",
            filterDefault: "Reset",
            filterDomestic: "Domestic only",
            filterOverviewType: "Show charts",
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
        },
    },
    zh: {
        translation: {
            countryCode: "{{countryName, country}}",
            visaStatus: "签证预约状态",
            sysStatus: "系统当前状态",
            checkee: "签证结果统计",
            filterDesc: "选择使馆/领事馆",
            filterSystemDesc: "选择系统：",
            filterDefault: "恢复默认",
            filterDomestic: "只看国内",
            filterOverviewType: "图表展示",
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
