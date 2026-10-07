import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useNilmStore = defineStore('nilm', () => {
  const appliances = ref([])
  const selectedDataset = ref('ukdale')
  const selectedModel = ref('proposed')
  const drawerVisible = ref(false)
  const buildingId = ref(Number(localStorage.getItem('building_id') || 1))
  const meterId = ref(Number(localStorage.getItem('meter_id') || 101))
  const buildings = ref([])
  const meters = ref([])

  const powerLimit = ref(3000)
  const alertCount = ref(0)
  const language = ref(localStorage.getItem('lang') || 'zh')

  const activeDevicesCount = computed(() => appliances.value.filter((a) => a.state).length)
  const totalDevicesCount = computed(() => appliances.value.length)
  const calculatedMainsPower = computed(() =>
    appliances.value.reduce((sum, a) => sum + (a.state ? a.power : 0), 0)
  )

  const toggleDrawer = () => {
    drawerVisible.value = !drawerVisible.value
  }

  const setLanguage = (lang) => {
    language.value = lang
    localStorage.setItem('lang', lang)
  }

  const setMeterId = (id) => {
    meterId.value = id
    localStorage.setItem('meter_id', String(id))
  }

  const setBuildingId = (id) => {
    buildingId.value = id
    localStorage.setItem('building_id', String(id))
  }

  return {
    appliances,
    selectedDataset,
    selectedModel,
    drawerVisible,
    buildingId,
    meterId,
    buildings,
    meters,
    powerLimit,
    alertCount,
    language,
    activeDevicesCount,
    totalDevicesCount,
    calculatedMainsPower,
    toggleDrawer,
    setLanguage,
    setMeterId,
    setBuildingId
  }
})
