import { createSlice } from "@reduxjs/toolkit";
import { getDetailVisaStatus } from "../services";
import { getDateFromISOString } from "../utils/misc";

const visastatusDetailSlice = createSlice({
    name: "visastatusDetail",
    initialState: {
        F: { timeRange: [], detail: {} },
        B: { timeRange: [], detail: {} },
        H: { timeRange: [], detail: {} },
        O: { timeRange: [], detail: {} },
        L: { timeRange: [], detail: {} },
    },
    reducers: {
        updateDeatil: (state, action) => {
            const { visaType, timeRange, detail } = action.payload;
            state[visaType].timeRange = timeRange;
            detail.forEach(({ embassyCode, availableDates }) => {
                state[visaType].detail[embassyCode] = availableDates;
            });
        },
    },
});

const { reducer, actions } = visastatusDetailSlice;
export const { updateDeatil } = actions;

export const fetchVisaStatusDetail = (visaType, embassyCode) => async dispatch => {
    if (Array.isArray(embassyCode) && embassyCode.length === 0) return Promise.resolve();
    try {
        const vsDetail = await getDetailVisaStatus(visaType, embassyCode, new Date());
        if (vsDetail) {
            const { timeRange, detail: rawDetail } = vsDetail;
            const detail = rawDetail.map(({ embassyCode: embassyCodeSingle, availableDates }) => ({
                embassyCode: embassyCodeSingle,
                availableDates: availableDates.map(({ writeTime, availableDate }) => ({
                    writeTime,
                    availableDate: availableDate === null ? null : getDateFromISOString(availableDate),
                })),
            }));
            dispatch(updateDeatil({ visaType, timeRange, detail }));
        }
    } catch (e) {
        console.error(`In fetchVisaStatusDetail: ${e}`);
    }

    return Promise.resolve();
};

export default reducer;
