import { useEffect } from "react";

export default function useScript(url) {
    useEffect(() => {
        const script = document.createElement("script");

        script.src = url;
        script.async = true;

        document.body.appendChild(script);

        return () => {
            document.body.removeChild(script);
        };
    }, [url]);
}
