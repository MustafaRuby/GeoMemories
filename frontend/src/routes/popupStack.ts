import { writable } from 'svelte/store';

// Stack di popup aperti, ogni elemento è una funzione di chiusura
export const popupStack = writable<Array<() => void>>([]);

export function pushPopup(onClose: () => void) {
    popupStack.update(stack => [...stack, onClose]);
}

export function popPopup() {
    popupStack.update(stack => stack.slice(0, -1));
}

export function closeTopPopup() {
    let closed = false;
    popupStack.update(stack => {
        if (stack.length > 0) {
            const top = stack[stack.length - 1];
            if (typeof top === 'function') top();
            closed = true;
            return stack.slice(0, -1);
        }
        return stack;
    });
    return closed;
}
