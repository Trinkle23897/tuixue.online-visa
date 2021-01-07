import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { fetchMetadata } from "../redux/metadataSlice";
import { fetchVisaStatusOverview } from "../redux/visastatusOverviewSlice";
import { fetchVisaStatusDetail } from "../redux/visastatusDetailSlice";
import { getCookie } from "../utils/cookie";

export default function useInitialDataFetch() {
    const dispatch = useDispatch();
    const visaType = getCookie("visaType", "F");
    useEffect(() => {
        const giganticFetch = async () => {
            await dispatch(fetchMetadata()); // Metadata fetch must finish before other fetch starts

            dispatch(fetchVisaStatusOverview(visaType));
            dispatch(fetchVisaStatusDetail(visaType));
        };

        giganticFetch();
    }, [dispatch, visaType]);
}
