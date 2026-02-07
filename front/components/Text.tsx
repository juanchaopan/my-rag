import PropText from "@/types/propText";

export default function Text(
    prop: PropText
        & { className?: string }
        & { onChange?: (text: string) => void }
        & { onSend?: () => void }
) {
    return (
        <div className={`w-full h-36 flex flex-row items-center 
         gap-3 px-4 py-3 border-t border-slate-200 bg-white/80 backdrop-blur supports-backdrop-filter:bg-white/60 ${prop.className ?? ""}`}>
            <textarea className="grow h-full resize-none
             rounded-xl border border-slate-200 bg-white p-3 text-sm leading-6 text-slate-900 shadow-sm focus:outline-none focus:ring-2 focus:ring-slate-400/30 focus:border-slate-300 disabled:bg-slate-50 disabled:text-slate-500 disabled:shadow-none"
                disabled={prop.isLocked}
                value={prop.text}
                onChange={(e) => prop.onChange?.(e.target.value)} />
            <button className="w-10 h-10
             shrink-0 rounded-xl border border-slate-200 bg-slate-900 text-white shadow-sm transition-colors hover:bg-slate-800 active:bg-slate-950 focus:outline-none focus:ring-2 focus:ring-slate-400/30"
                onClick={() => prop.onSend?.()}>√</button>
        </div>
    );
}