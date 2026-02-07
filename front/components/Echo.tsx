import PropEcho from "@/types/propEcho";

export default function Echo(
    prop: PropEcho
) {
    return (
        <>
            <div className="w-fit max-w-[95%] h-fit self-end
             px-4 py-2 rounded-2xl bg-slate-900 text-slate-50 shadow-sm whitespace-pre-wrap wrap-break-word text-sm leading-6">{prop.userContent}</div>
            <div className="w-fit max-w-[95%] h-fit self-start
             px-4 py-2 rounded-2xl bg-slate-100 text-slate-900 border border-slate-200 shadow-sm whitespace-pre-wrap wrap-break-word text-sm leading-6">{prop.assistantContent}</div>
        </>
    )
}