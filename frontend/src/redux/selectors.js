import { createSelector } from "@reduxjs/toolkit";
import { findEmbassyAttributeByCode, findEmbassyAttributeByAnotherAttr } from "../utils/USEmbassy";

const metadataSelector = state => state.metadata;
const overviewSelector = state => state.visastatusOverview;
const newestSelector = state => state.visastatusNewest;
const filterSelector = state => state.visastatusFilter;

const embassyLstSelector = createSelector(metadataSelector, metadata => metadata.embassyLst);
const makeOverviewSelectorByVisaType = visaType => createSelector(overviewSelector, overview => overview[visaType]);
const makeNewestSelectorByVisaType = visaType => createSelector(newestSelector, newest => newest[visaType]);
const makeFilterSelectorByVisaType = visaType => createSelector(filterSelector, filter => filter[visaType]);

export const makeOverviewDetailSelector = visaType =>
    createSelector(
        [embassyLstSelector, makeOverviewSelectorByVisaType(visaType), makeFilterSelectorByVisaType(visaType)],
        (embLst, overview, filter) => {
            if (overview.length > 0) {
                const overviewLst = overview[0].overview;
                return overviewLst
                    .filter(ov => filter.includes(ov.embassyCode))
                    .map(ov =>
                        Object.fromEntries(
                            Object.entries(ov).map(([k, v]) =>
                                k === "embassyCode"
                                    ? ["embassyName", findEmbassyAttributeByCode("nameEn", v, embLst)]
                                    : [k, v],
                            ),
                        ),
                    );
            }
        },
    );

export const makeNewestVisaStatusSelector = (visaType, embassyName) =>
    createSelector([embassyLstSelector, makeNewestSelectorByVisaType(visaType)], (embLst, newest) => {
        const targetNewest = newest.find(
            ({ embassyCode }) =>
                findEmbassyAttributeByAnotherAttr("nameEn", "code", embassyCode, embLst) === embassyName,
        );
        return targetNewest;
    });
