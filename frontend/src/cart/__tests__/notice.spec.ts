import { mount } from '@vue/test-utils'
import { afterEach, expect, it, vi } from 'vitest'
import CartNotice from '../presentation/CartNotice.vue'
import { i18n } from '@/i18n'
afterEach(()=>vi.useRealTimers())
it('expires after three seconds, pauses for hover and focus, and restarts on each action',async()=>{
 vi.useFakeTimers()
 const wrapper=mount(CartNotice,{props:{message:'Added',event:{}},global:{plugins:[i18n]}})
 await vi.advanceTimersByTimeAsync(1000)
 await wrapper.trigger('mouseenter')
 await vi.advanceTimersByTimeAsync(5000)
 expect(wrapper.emitted('dismiss')).toBeUndefined()
 await wrapper.trigger('mouseleave')
 await vi.advanceTimersByTimeAsync(1900)
 expect(wrapper.emitted('dismiss')).toBeUndefined()
 await wrapper.setProps({event:{}})
 await vi.advanceTimersByTimeAsync(2999)
 expect(wrapper.emitted('dismiss')).toBeUndefined()
 await vi.advanceTimersByTimeAsync(1)
 expect(wrapper.emitted('dismiss')).toHaveLength(1)
 await wrapper.setProps({event:{}})
 await wrapper.trigger('focusin')
 await vi.advanceTimersByTimeAsync(5000)
 expect(wrapper.emitted('dismiss')).toHaveLength(1)
 await wrapper.trigger('focusout',{relatedTarget:null})
 await vi.advanceTimersByTimeAsync(3000)
 expect(wrapper.emitted('dismiss')).toHaveLength(2)
 wrapper.unmount()
})
