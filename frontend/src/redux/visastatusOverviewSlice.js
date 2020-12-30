import { createSlice } from "@reduxjs/toolkit";
import { getVisaStatusOverview } from "../services";
import { getDateFromISOString } from "../utils/misc";

const visastatusOverviewSlice = createSlice({
    name: "visastatusOverview",
    initialState: { today: { F: [], B: [], O: [], H: [], L: [] }, span: { F: [], B: [], H: [], O: [], L: [] } },
    reducers: {
        updateOverview: (state, action) => {
            const { visaType, overviewLstToday, overviewLstSpan } = action.payload;
            overviewLstToday.forEach(overview => {
                const overviewIdx = state.today[visaType].findIndex(ov => ov.embassyCode === overview.embassyCode);
                if (overviewIdx !== -1) {
                    state.today[visaType][overviewIdx] = overview;
                } else {
                    state.today[visaType].push(overview);
                }
            });
            state.span[visaType] = overviewLstSpan;
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
    const past = new Date();
    past.setDate(now.getDate() - 60);
    try {
        const vsOverview = await getVisaStatusOverview(visaType, selectedEmb, past, now);
        if (vsOverview) {
            const { visaStatus } = vsOverview;
            const overviewLstToday = visaStatus[0].overview.map(({ embassyCode, earliestDate, latestDate }) => ({
                visaType,
                embassyCode,
                earliestDate: getDateFromISOString(earliestDate),
                latestDate: getDateFromISOString(latestDate),
            }));
            dispatch(updateOverview({ visaType, overviewLstToday, overviewLstSpan: visaStatus }));
        }
    } catch (e) {
        console.error(`In fetchVisaStatusOverview: ${e}`);
    }

    return Promise.resolve();
};

export default reducer;
