"use client"
import Messages from "@/components/Messages";
import Text from "@/components/Text";
import useChat from "@/hooks/useChat";
import useChatStore from "@/stores/useChatStore";

export default function Home() {
  const text = useChatStore((state) => state.text);
  const isLocked = useChatStore((state) => state.isLocked);
  const echoes = useChatStore((state) => state.echoes);
  const setText = useChatStore((state) => state.setText);
  const setLocked = useChatStore((state) => state.setLocked);
  const setEchoes = useChatStore((state) => state.setEchoes);
  const appendEchoTokenAt = useChatStore((state) => state.appendEchoTokenAt);
  const { sendMessage } = useChat();
  return (
    <div className="w-full h-fit flex flex-col">
      <Messages echoes={echoes} />
      <Text text={text} isLocked={isLocked} onChange={setText}
        onSend={() => {
          const newEcho = { userContent: text, assistantContent: "" };
          const newEchoes = [...echoes, newEcho];
          setText("");
          setLocked(true);
          setEchoes(newEchoes);
          sendMessage(newEchoes, (token) => appendEchoTokenAt(newEchoes.length - 1, token), () => setLocked(false));
        }} />
    </div>
  );
}
