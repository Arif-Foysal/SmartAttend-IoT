<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-800 mb-6">Attendance Log</h1>
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <table class="w-full text-left text-sm text-gray-600">
        <thead class="bg-gray-50 border-b border-gray-100">
          <tr>
            <th class="px-6 py-4 font-semibold">Student Name</th>
            <th class="px-6 py-4 font-semibold">Time</th>
            <th class="px-6 py-4 font-semibold">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="log in logs" :key="log.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 font-medium text-gray-800">{{ log.student ? log.student.name : 'Unknown' }}</td>
            <td class="px-6 py-4">{{ new Date(log.timestamp).toLocaleString() }}</td>
            <td class="px-6 py-4">
              <span class="bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs">Present</span>
            </td>
          </tr>
          <tr v-if="logs.length === 0">
            <td colspan="3" class="px-6 py-4 text-center text-gray-400">No records found.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const logs = ref<any[]>([])

const fetchLogs = async () => {
    try {
        const { data } = await useFetch('http://localhost:8000/attendance/')
        if (data.value) {
            logs.value = data.value as any[]
        }
    } catch (e) {
        console.error("Error fetching attendance", e)
    }
}

fetchLogs()
</script>
