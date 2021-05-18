import { createSelector } from "@reduxjs/toolkit";
import { dateDiff } from "../utils/misc";
import { embassyAttributeIdx, findEmbassyAttributeByCode } from "../utils/USEmbassy";

// basic selectors
const metadataSelector = state => state.metadata;
const overviewTodaySelector = state => state.visastatusOverview.today;
const overviewSpanSelector = state => state.visastatusOverview.span;
const newestSelector = state => state.visastatusNewest;
const filterSelector = state => state.visastatusFilter;
const detailSelector = state => state.visastatusDetail;

const embassyLstSelector = createSelector(metadataSelector, metadata => metadata.embassyLst);
const qqTgInfoSelector = createSelector(metadataSelector, metadata => metadata.qqTgInfo);
export const nonDomesticEmbassyInDefaultFilterSelector = createSelector(
    metadataSelector,
    metadata => metadata.nondomesticDefaultFilter,
);

export const makeCountryCodeSelector = embassyCode =>
    createSelector(embassyLstSelector, embassyLst => findEmbassyAttributeByCode("country", embassyCode, embassyLst));

export const makeEmbassyBySysSelector = sys =>
    createSelector(embassyLstSelector, embassyLst =>
        sys === "all"
            ? embassyLst.map(emb => emb[embassyAttributeIdx.code])
            : embassyLst.filter(emb => emb[embassyAttributeIdx.sys] === sys).map(emb => emb[embassyAttributeIdx.code]),
    );
const embassyOptionsSelector = createSelector(embassyLstSelector, embassyLst =>
    embassyLst.map(emb => ({ name: emb[embassyAttributeIdx.nameEn], code: emb[embassyAttributeIdx.code] })),
);
const rceTreeSelector = createSelector(metadataSelector, metadata => metadata.regionCountryEmbassyTree);
export const makeEmbassyTreeSelector = (sys, t, forFilterSelect = true) =>
    createSelector(
        [embassyOptionsSelector, rceTreeSelector, makeEmbassyBySysSelector(sys)],
        (embassyOptions, rceTree, embassyBySys) =>
            rceTree
                .map(({ region, countryEmbassyMap }) => ({
                    title: t(region),
                    value: region,
                    key: region,
                    selectable: forFilterSelect,
                    children: countryEmbassyMap
                        .map(({ country, embassyCodeLst }) => ({
                            title: t(country),
                            value: country,
                            key: country,
                            selectable: forFilterSelect,
                            children: embassyOptions
                                .filter(({ code }) => embassyCodeLst.includes(code) && embassyBySys.includes(code))
                                .map(({ code }) => ({ title: t(code), value: code, key: code })),
                        }))
                        .filter(countryNode => countryNode.children.length > 0),
                }))
                .filter(regionNode => regionNode.children.length > 0),
    );

// generate `make{Some}SelectorByVisaType`
const makeSelectorMakerByVisaType = selector => visaType =>
    createSelector(selector, output => {
        if (visaType !== "F" && Array.isArray(output[visaType]))
            return output[visaType].filter(e => e !== "bju" && e !== "shu" && e !== "syu" && e !== "gzu");
        return output[visaType];
    });

// Selectors by Visa type
const makeOverviewSelectorByVisaType = makeSelectorMakerByVisaType(overviewTodaySelector);
export const makeFilterSelectorByVisaType = makeSelectorMakerByVisaType(filterSelector);
export const makeDetailSelectorByVisaType = makeSelectorMakerByVisaType(detailSelector);
export const makeOverviewSpanSelectorByVisaType = makeSelectorMakerByVisaType(overviewSpanSelector);
export const makeOverviewDetailSelector = visaType =>
    createSelector(
        [makeOverviewSelectorByVisaType(visaType), makeFilterSelectorByVisaType(visaType)],
        (overview, filter) =>
            filter.map(
                code =>
                    overview.find(ov => ov.embassyCode === code) || {
                        visaType,
                        embassyCode: code,
                        earliestDate: ["/"],
                        latestDate: ["/"],
                    },
            ),
    );

export const makeNewestVisaStatusSelector = (visaType, embassyCode) =>
    createSelector(newestSelector, newest => newest[visaType][embassyCode]);

export const makeQqTgInfoSelector = embassyCode =>
    createSelector([embassyLstSelector, qqTgInfoSelector], (embassyLst, { qq, tg }) => {
        const region = findEmbassyAttributeByCode("region", embassyCode, embassyLst);
        const index = region === "DOMESTIC" ? "domestic" : "nonDomestic";
        return [qq[index], tg[index]];
    });

// Selectors for echart data
export const makeMinuteChartData = visaType =>
    createSelector(
        [makeDetailSelectorByVisaType(visaType), makeFilterSelectorByVisaType(visaType)],
        (rawData, vsFilter) => {
            const delta = 60000;
            const { timeRange, detail } = rawData;
            if (timeRange.length === 0) {
                return [[], [], []];
            }
            const [tsStart, tsEnd] = timeRange;
            const writeTime = [];
            for (let t = tsStart - delta; t <= tsEnd; t += delta) {
                writeTime.push(t);
            }
            const availDateLst = vsFilter.map(embassyCode => {
                const availableDates = detail[embassyCode] || [];
                let dataIndex = 0;
                let current = null;
                const avaDates = writeTime.map(t => {
                    if (dataIndex < availableDates.length && availableDates[dataIndex].writeTime === t) {
                        current = availableDates[dataIndex].availableDate;
                        dataIndex += 1;
                    }
                    return current === null ? null : current.join("/");
                });
                return { embassyCode, availableDates: avaDates };
            });
            return [writeTime, availDateLst];
        },
    );

export const makeDateChartData = (visaType, embassyCode) =>
    createSelector([makeOverviewSpanSelectorByVisaType(visaType)], rawData => {
        const chartData = rawData
            .slice()
            .reverse()
            .map(({ date, overview }, index) => {
                const earliestDateObj = {};
                const latestDateObj = {};
                overview.forEach(({ embassyCode: e, earliestDate, latestDate }) => {
                    earliestDateObj[e] = earliestDate;
                    latestDateObj[e] = latestDate;
                });
                const earliestDateLst = earliestDateObj[embassyCode] || null;
                const latestDateLst = latestDateObj[embassyCode] || null;
                return [index, date, earliestDateLst, latestDateLst];
            });
        const earliestDateDiffLst = chartData.filter(e => e[2] !== null).map(e => dateDiff(e[1], e[2]));
        const latestDateDiffLst = chartData.filter(e => e[3] !== null).map(e => dateDiff(e[1], e[3]));
        const getAvg = arr => (arr.length >= 10 ? (arr.reduce((acc, c) => acc + c, 0) / arr.length).toFixed(0) : null);
        return [chartData, getAvg(earliestDateDiffLst), getAvg(latestDateDiffLst)];
    });
