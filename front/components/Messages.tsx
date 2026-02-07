import PropMessages from "@/types/propMessages";
import Echo from "./Echo";

export default function Messages(
    prop: PropMessages
        & { className?: string }
) {
    return (
        <div className={`w-full h-fit flex flex-col
         gap-3 px-4 py-3 ${prop.className ?? ""}`}>
            {prop.echoes.map((echo, index) => <Echo key={index} {...echo} />)}
        </div>
    );
}