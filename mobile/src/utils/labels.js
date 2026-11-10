const APPLIANCE_LABELS = {
  fridge: 'Refrigerator',
  kettle: 'Electric Kettle',
  microwave: 'Microwave',
  dishwasher: 'Dishwasher',
  washing_machine: 'Washing Machine'
}

export function applianceLabel(type, fallback) {
  return APPLIANCE_LABELS[type] || fallback || type || 'Appliance'
}

export function applianceKey(type) {
  return type === 'washing_machine' ? 'washingMachine' : type
}

export const ALERT_LABELS = {
  overload: 'Mains Overload',
  info: 'System Notice',
  warning: 'Warning',
  danger: 'Danger'
}

export function alertTitle(alert) {
  return alert?.title_en || alert?.title || ALERT_LABELS[alert?.type] || 'Alert'
}

export function alertMessage(alert) {
  return alert?.message_en || alert?.message || ''
}
