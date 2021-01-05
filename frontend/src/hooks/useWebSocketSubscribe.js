import { useEffect, useRef, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { updateNewest } from "../redux/visastatusNewestSlice";
import { openLatestVisaStatusSocket } from "../services";
import { renameObjectKeys, getDateFromISOString } from "../utils/misc";

const ONE_MINUTE = 60 * 1000;
let CONNECT_ATTEMPT = 0;

export default function useWebSocketSubscribe() {
    const [t] = useTranslation();
    const dispatch = useDispatch();
    const visastatusTab = useSelector(state => state.visastatusTab);
    const visastatusFilter = useSelector(state => state.visastatusFilter);
    const embassyLst = useSelector(state => state.metadata.embassyLst);
    const visaTypeDetails = useSelector(state => state.metadata.visaTypeDetails);
    const [wsConnected, setWsConnected] = useState(false);
    const websocketRef = useRef(null); // initiate with null doesn't trigger re-connect when re-renderin
    const [notificationTitle, setNotificationTitle] = useState(t("notificationInitTitle"));
    const [notificationOption, setNotificationOption] = useState({ body: t("notificationInitContent") });
    const notifDateStr = s => {
        const date = getDateFromISOString(s).map(e => parseInt(e, 10));
        const now = new Date();
        return date[0] === now.getFullYear() ? date.slice(1).join("/") : date.join("/");
    };

    // This effect SHOULD keep web socket alive and reconnect when it's closed
    useEffect(() => {
        if (!wsConnected && (websocketRef.current === null || websocketRef.current.readyState === WebSocket.CLOSED)) {
            websocketRef.current = openLatestVisaStatusSocket();
            CONNECT_ATTEMPT += 1;
            console.log(`Connect WebSocket for the ${CONNECT_ATTEMPT} times`);
        }

        websocketRef.current.onopen = () => setWsConnected(true);
        websocketRef.current.onclose = () => setWsConnected(false);
        websocketRef.current.onerror = e => console.error(`Error from websocketRef: ${e}`);
        websocketRef.current.onmessage = e => {
            const { type, data } = renameObjectKeys(JSON.parse(e.data));
            if (type === "notification") {
                const { visaType, embassyCode, prevAvaiDate, currAvaiDate } = data;
                const visaTypeDetail = visaTypeDetails[visaType];

                // only send notification for selected visa type and embassy
                if (visastatusTab === visaType && visastatusFilter[visaType].includes(embassyCode)) {
                    setNotificationTitle(t("notificationTitle", { visaTypeDetail }));
                    setNotificationOption({
                        body: t("notificationContent", {
                            embassyName: t(embassyCode),
                            prevAvaiDate: prevAvaiDate ? notifDateStr(prevAvaiDate) : "/",
                            currAvaiDate: notifDateStr(currAvaiDate),
                        }),
                    });
                }
            } else if (type === "newest") {
                if (data.length > 0) {
                    const { visaType } = data[0];
                    dispatch(updateNewest({ visaType, newest: data }));
                }
            }
        };
    }, [embassyLst, visaTypeDetails, wsConnected, dispatch, t, visastatusTab, visastatusFilter]);

    useEffect(() => {
        if (wsConnected) {
            const getNewestVisaStatus = visaType =>
                websocketRef.current.readyState === WebSocket.OPEN &&
                websocketRef.current.send(JSON.stringify([visaType, visastatusFilter[visaType]]));

            Array.from("FBOHL").forEach(visaType => getNewestVisaStatus(visaType));

            const intervalIds = Array.from("FBOHL").map(visaType =>
                setInterval(() => getNewestVisaStatus(visaType), ONE_MINUTE),
            );
            return () => intervalIds.forEach(intvId => clearInterval(intvId));
        }
    }, [wsConnected, visastatusFilter]);

    return [notificationTitle, notificationOption];
}
