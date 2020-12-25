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
            overviewTitle: "Visa Status Overview",
            visaType: "Visa Type {{visaType}}",
            filterDesc: "Add embassies/consulates of your choice",
            filterSystemDesc: "Filter by system: ",
            filterDefault: "Reset to default",
            filterDomestic: "Domestic only",
            all: "All",
            overviewRange: "The changing range of Earliest Date within 24h",
            overviewNewest: "The current Earliest Date",
            overviewEmailIcon: "Subscribe from email",
            overviewQQIcon: "Subscribe from QQ group / Telegram channel",
            overviewAddtionalIcon: "Additional information",
        },
    },
    zh: {
        translation: {
            countryCode: "{{countryName, country}}",
            visaStatus: "签证预约状态",
            sysStatus: "系统当前状态",
            checkee: "签证结果统计",
            overviewTitle: "美国签证预约时间",
            visaType: "{{visaType}}签",
            filterDesc: "选择使馆/领事馆",
            filterSystemDesc: "选择系统：",
            filterDefault: "恢复默认",
            filterDomestic: "只看国内",
            at: "于",
            all: "全部",
            overviewRange: "过去24h内最早预约日期变化范围",
            overviewNewest: "当前日期",
            overviewEmailIcon: "邮件订阅",
            overviewQQIcon: "QQ群/Telegram频道订阅",
            overviewAddtionalIcon: "更多信息",
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
