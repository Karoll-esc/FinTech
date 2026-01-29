import { createContext, useContext, useMemo, useState, ReactNode } from 'react';
import Toast from './Toast';

type ToastItem = { id: string; title?: string; message: string; type?: 'info'|'success'|'error'|'warning' };
const NOOP = { add: (_m?:string,_t?:any,_title?:string)=>{}, remove: (_id?:string)=>{} };
const ToastContext = createContext<any>(NOOP);
export const useToast = () => useContext(ToastContext);

export function ToastProvider({ children }: { children: ReactNode }){
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const add = (message: string, type: ToastItem['type']='info', title?: string)=>{
    const id = `${Date.now()}-${Math.random().toString(36).slice(2,8)}`;
    setToasts(t=>[...t,{id,title,message,type}]);
  };
  const remove = (id:string)=> setToasts(t=>t.filter(x=>x.id!==id));
  const value = useMemo(()=>({ add, remove }), []);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-3">
        {toasts.map(t=> <Toast key={t.id} id={t.id} title={t.title} message={t.message} type={t.type} onClose={remove} />)}
      </div>
    </ToastContext.Provider>
  );
}

export default ToastProvider;
