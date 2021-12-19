import React from 'react';

export enum NotifyType {
     "error" = 1,
     "success",
     "info"
}

type NotificationContextType = {
  notifications: NotificationProps[];
  addNotification: (type: NotifyType, msg: string) => void;
  clearNotification: (id: string) => void;
};

type NotificationProps = {
    id: string;
    type: NotifyType;
    msg: string;
    time: number;
}

export const NotificationContext = React.createContext<NotificationContextType>({
    notifications: [],
    addNotification: (type: NotifyType, msg: string) => {},
    clearNotification: (id: string) => {}
})

export function NotificationProvider({ children }: any) {

    const maxNotificationCount = 6
    const notificationAliveTime = 10 //Seconds

    const [notifications, setNotifications] = React.useState<NotificationProps[]>([]);

    const addNotification = (type: NotifyType, msg: string) => {
        const notification =  {id: Math.random().toString(16), type: type, msg: msg, time: 0};

        setNotifications(oldNotifications => {
            let notificationsCopy = oldNotifications.slice()
            notificationsCopy.push(notification)
            if(notificationsCopy.length > maxNotificationCount) {
                notificationsCopy.splice(0, 1)
            }
            return notificationsCopy
        });
    }

    const clearNotification = (id: string) => {
        setNotifications(oldNotifications => {
            let notificationsCopy = oldNotifications.slice()
            const index = notificationsCopy.findIndex(element => element.id === id)
            if(index > -1) {
                notificationsCopy.splice(index, 1)
            }
            return notificationsCopy
        });
    }

    const updateNotifications = () => {
        setNotifications(oldNotifications => {
            let notificationsCopy = oldNotifications.slice()
            let notificationsCleared: NotificationProps[] = []
            notificationsCopy.forEach(element => {
                element.time += 1
                if(element.time < notificationAliveTime) {
                    notificationsCleared.push(element)
                }
            })
            return notificationsCleared
        });
    }

    React.useEffect(() => {
        const interval = setInterval(() => {
            updateNotifications()
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    const contextValue: NotificationContextType = {
        notifications: notifications,
        addNotification: React.useCallback((type: NotifyType, msg: string) => addNotification(type, msg), []),
        clearNotification: React.useCallback((id: string) => clearNotification(id), [])
    }

    return <NotificationContext.Provider value={contextValue}>{children}</NotificationContext.Provider>
}

export function NotificationOutlet() {
    const { notifications } = React.useContext(NotificationContext)
  
    var notificationsContent = notifications.map(notification => (
        <Notification key={notification.id} {...notification}/>
    ));

    return (
    <div aria-live="polite" aria-atomic="true" className="position-relative" style={{"zIndex": 999}}>
        <div className="toast-container position-absolute top-0 end-0 p-3">
            {notificationsContent}
        </div>
    </div>
    );
  }
  
export function Notification(props: NotificationProps) {
    const { clearNotification } = React.useContext(NotificationContext)

    var toastHeader = ""
    var toastTitle = ""
    if(props.type === NotifyType.success) {
        toastHeader = "toast-header bg-success text-white"
        toastTitle = "Success"
    } else if(props.type === NotifyType.info) {
        toastHeader = "toast-header bg-primary text-white"
        toastTitle = "Info"
    } else { //else and error
        toastHeader = "toast-header bg-danger text-white"
        toastTitle = "Error"
    }

    return (
    <div className="toast show" role="alert" aria-live="assertive" aria-atomic="true">
        <div className={toastHeader} >
            <strong className="me-auto">{toastTitle}</strong>
            <button type="button" className="btn-close" onClick={() => clearNotification(props.id)}></button>
        </div>
        <div className="toast-body">
            {props.msg}
        </div>
    </div>
    );
}

