import { useCallback } from "react";
import PropEcho from "@/types/propEcho";

export default function useChat() {
    const sendMessage = useCallback(async (
        echoes: PropEcho[],
        onToken?: (token: string) => void,
        onComplete?: () => void,
    ) => {
        const response = await fetch(`${process.env.CHAT_URL}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(echoes.map(echo => [{ role: "user", content: echo.userContent }, { role: "assistant", content: echo.assistantContent }]).flat()),
        });
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        while (reader) {
            const { done, value } = await reader.read();
            if (done) {
                onComplete?.();
                break;
            } else {
                const token = decoder.decode(value);
                onToken?.(token);
            }
        };
    }, []);
    return {
        sendMessage,
    };
}