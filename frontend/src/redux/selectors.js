import { createSelector } from "@reduxjs/toolkit";
import { embassyAttributeIdx, findEmbassyAttributeByCode } from "../utils/USEmbassy";
import i18n from "../utils/i18n";

// basic selectors
const metadataSelector = state => state.metadata;
const overviewSelector = state => state.visastatusOverview;
const newestSelector = state => state.visastatusNewest;
const filterSelector = state => state.visastatusFilter;
const embassyLstSelector = createSelector(metadataSelector, metadata => metadata.embassyLst);
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
export const makeEmbassyTreeSelector = sys =>
    createSelector(
        [embassyOptionsSelector, rceTreeSelector, makeEmbassyBySysSelector(sys)],
        (embassyOptions, rceTree, embassyBySys) =>
            rceTree
                .map(({ region, countryEmbassyMap }) => ({
                    title: region
                        .split("_")
                        .map(s => `${s[0]}${s.slice(1).toLowerCase()}`)
                        .join(" "),
                    value: region,
                    key: region,
                    children: countryEmbassyMap
                        .map(({ country, embassyCodeLst }) => ({
                            title: i18n.t("countryCode", { countryName: country }), // no change when i18n lng changes, should be fixed
                            value: country,
                            key: country,
                            children: embassyOptions
                                .filter(({ code }) => embassyCodeLst.includes(code) && embassyBySys.includes(code))
                                .map(emb => ({ title: emb.name, value: emb.code, key: emb.code })),
                        }))
                        .filter(countryNode => countryNode.children.length > 0),
                }))
                .filter(regionNode => regionNode.children.length > 0),
    );

// generate `make{Some}SelectorByVisaType`
const makeSelectorMakerByVisaType = selector => visType => createSelector(selector, output => output[visType]);

// Selectors by Visa type
const makeOverviewSelectorByVisaType = makeSelectorMakerByVisaType(overviewSelector);
export const makeFilterSelectorByVisaType = makeSelectorMakerByVisaType(filterSelector);

export const makeOverviewDetailSelector = visaType =>
    createSelector(
        [embassyLstSelector, makeOverviewSelectorByVisaType(visaType), makeFilterSelectorByVisaType(visaType)],
        (embLst, overview, filter) =>
            overview
                .filter(ov => filter.includes(ov.embassyCode))
                .map(ov => ({ ...ov, embassyName: findEmbassyAttributeByCode("nameEn", ov.embassyCode, embLst) })),
    );

export const makeNewestVisaStatusSelector = (visaType, embassyCode) =>
    createSelector(newestSelector, newest => newest[visaType][embassyCode]);
