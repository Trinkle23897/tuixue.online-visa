import { useEffect, useRef } from "react";

let i = 0;

export default function useTestHook() {
    const testRef = useRef(0);

    useEffect(() => {
        const intvId = setInterval(() => {
            testRef.current += i;
            i += 1;
        }, 5000);
        return () => clearInterval(intvId);
    });

    useEffect(() => {
        const intvId = setInterval(() => console.log(testRef), 5000);
        return () => clearInterval(intvId);
    });
}
