import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { fetchMetadata } from "../redux/metadataSlice";
import { fetchVisaStatusOverview } from "../redux/visastatusOverviewSlice";

export default function useInitialDataFetch() {
    const dispatch = useDispatch();
    useEffect(() => {
        const giganticFetch = async () => {
            await dispatch(fetchMetadata()); // Metadata fetch must finish before other fetch starts
            Array.from("FBHOL").forEach(vt => dispatch(fetchVisaStatusOverview(vt)));
        };

        giganticFetch();
    }, [dispatch]);
}
