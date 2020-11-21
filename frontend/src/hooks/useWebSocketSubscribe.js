import { useEffect, useRef, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { notification } from "antd";
import { updateNewest } from "../redux/visastatusNewest";
import { openLatestVisaStatusSocket } from "../services";
import { renameObjectKeys } from "../utils/misc";

const ONE_MINUTE = 60 * 1000;
let CONNECT_ATTEMPT = 0;

export default function useWebSocketSubscribe() {
    const dispatch = useDispatch();
    const visastatusFilter = useSelector(state => state.visastatusFilter);
    const [wsConnected, setWsConnected] = useState(false);
    const websocketRef = useRef(null); // initiate with null doesn't trigger re-connect when re-renderin

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
                console.log(`${new Date()} Sending notification pop up`);
                console.log(data);
                notification.warn({
                    message: `${data.visaType}: Visa Status Change ${data.embassyCode}`,
                    description: `${data.embassyCode} changed from ${data.prevAvaiDate || "/"} to ${data.currAvaiDate}`,
                    duration: 3,
                    placement: "topRight",
                });
            } else if (type === "newest") {
                if (data.length > 0) {
                    const { visaType } = data[0];
                    dispatch(updateNewest({ visaType, newest: data }));
                }
            }
        };
    }, [wsConnected, dispatch]);

    useEffect(() => {
        // We don't need to check wsConnect here because WebSocket.readyState must be OPEN to
        // send a message.
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
}
