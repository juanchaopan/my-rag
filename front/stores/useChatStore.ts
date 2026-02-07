import PropEcho from "@/types/propEcho";
import { create } from "zustand/react";

interface ChatStore {
    text: string;
    isLocked: boolean;
    echoes: PropEcho[];
    setText(text: string): void;
    setLocked(locked: boolean): void;
    setEchoes(echoes: PropEcho[]): void;
    appendEchoTokenAt(index: number, token: string): void;
}

const useChatStore = create<ChatStore>((set) => ({
    text: "",
    isLocked: false,
    echoes: [],
    setText(text: string) {
        set({ text });
    },
    setLocked(locked: boolean) {
        set({ isLocked: locked });
    },
    setEchoes(echoes: PropEcho[]) {
        set({ echoes });
    },
    appendEchoTokenAt(index: number, token: string) {
        set(state => ({
            echoes: state.echoes.map((echo, i) =>
                i === index
                    ? {
                        ...echo,
                        assistantContent: echo.assistantContent + token,
                    }
                    : echo
            ),
        }));
    }
}));

export default useChatStore;