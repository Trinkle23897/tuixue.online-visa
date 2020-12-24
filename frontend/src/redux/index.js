import { configureStore } from "@reduxjs/toolkit";
import metadata from "./metadataSlice";
import visastatusNewest from "./visastatusNewestSlice";
import visastatusFilter from "./visastatusFilterSlice";
import visastatusOverview from "./visastatusOverviewSlice";
import visastatusTab from "./visastatusTabSlice";
import visastatusDetail from "./visastatusDetailSlice";

export default configureStore({
    reducer: {
        metadata,
        visastatusNewest,
        visastatusFilter,
        visastatusOverview,
        visastatusTab,
        visastatusDetail,
    },
});
