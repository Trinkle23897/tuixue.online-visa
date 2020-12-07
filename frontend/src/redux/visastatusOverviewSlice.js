import { createSlice } from "@reduxjs/toolkit";
import { getVisaStatusOverview } from "../services";
import { getDateFromISOString } from "../utils/misc";

const visastatusOverviewSlice = createSlice({
    name: "visastatusOverview",
    initialState: { F: [], B: [], O: [], H: [], L: [] },
    reducers: {
        updateOverview: (state, action) => {
            const { visaType, overviewLst } = action.payload;
            overviewLst.forEach(overview => {
                const overviewIdx = state[visaType].findIndex(ov => ov.embassyCode === overview.embassyCode);
                if (overviewIdx !== -1) {
                    state[visaType][overviewIdx] = overview;
                } else {
                    state[visaType].push(overview);
                }
            });
        },
    },
});

const { reducer, actions } = visastatusOverviewSlice;
export const { updateOverview } = actions;

export const fetchVisaStatusOverview = visaType => async (dispatch, getState) => {
    const {
        visastatusFilter: { [visaType]: selectedEmb },
    } = getState();

    if (selectedEmb.length === 0) {
        return Promise.resolve();
    }

    const now = new Date();
    try {
        const vsOverview = await getVisaStatusOverview(visaType, selectedEmb, now, now);
        if (vsOverview) {
            const { visaStatus } = vsOverview;
            const overviewLst = visaStatus[0].overview.map(({ embassyCode, earliestDate, latestDate }) => ({
                visaType,
                embassyCode,
                earliestDate: getDateFromISOString(earliestDate),
                latestDate: getDateFromISOString(latestDate),
            }));
            dispatch(updateOverview({ visaType, overviewLst }));
        }
    } catch (e) {
        console.error(`In fetchVisaStatusOverview: ${e}`);
    }

    return Promise.resolve();
};

export default reducer;
