import { createSlice } from "@reduxjs/toolkit";
import { fetchVisaStatusDetail } from "./visastatusDetailSlice";
import { fetchVisaStatusOverview } from "./visastatusOverviewSlice";
import { setCookie } from "../utils/cookie";

const visastatusFilterSlice = createSlice({
    name: "visastatusFilter",
    initialState: { F: [], B: [], O: [], H: [], L: [] },
    reducers: {
        updateFilter: (state, action) => {
            const { visaType, newFilter } = action.payload;
            state[visaType] = newFilter;
        },
    },
});

const { reducer, actions } = visastatusFilterSlice;
export const { updateFilter } = actions;

export const updateFilterAndFetch = (visaType, newFilter) => async dispatch => {
    setCookie(`filter-${visaType}`, newFilter);
    dispatch(updateFilter({ visaType, newFilter }));
    dispatch(fetchVisaStatusOverview(visaType));
    dispatch(fetchVisaStatusDetail(visaType));
    return Promise.resolve();
};

export default reducer;
