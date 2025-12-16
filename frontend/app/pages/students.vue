<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">Students</h1>
      <button @click="openAddModal" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
        + Add Student
      </button>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">{{ isEditing ? 'Edit Student' : 'Register New Student' }}</h2>
        <form @submit.prevent="registerStudent" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Full Name</label>
            <input v-model="form.name" type="text" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2">
          </div>
          
          <!-- Image Gallery (Edit Mode) -->
          <div v-if="isEditing">
             <label class="block text-sm font-medium text-gray-700 mb-2">Training Images</label>
             <div class="grid grid-cols-3 gap-2 mb-4">
                 <div v-for="img in currentStudentImages" :key="img.id" class="relative group">
                     <img :src="`http://localhost:8000/images/${img.id}`" class="w-full h-24 object-cover rounded-lg border">
                     <button type="button" @click="deleteImage(img.id)" class="absolute top-1 right-1 bg-red-600 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                     </button>
                 </div>
             </div>
             <div>
                <label class="block text-xs font-medium text-gray-500 mb-1">Add New Image</label>
                <div class="flex gap-2">
                    <input ref="newImageInput" type="file" accept="image/*" class="text-sm text-gray-500 w-full">
                    <button type="button" @click="uploadNewImage" class="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">Upload</button>
                </div>
             </div>
          </div>

          <!-- Initial Photo (Create Mode) -->
          <div v-else>
            <label class="block text-sm font-medium text-gray-700">Photo</label>
            <input @change="handleFileUpload" type="file" accept="image/*" required class="mt-1 block w-full text-sm text-gray-500">
            <p class="text-xs text-gray-400 mt-1">Upload a clear face photo for encoding.</p>
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <button type="button" @click="showModal = false" class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Done</button>
            <button v-if="!isEditing" type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Register</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Table -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mt-6">
      <table class="w-full text-left text-sm text-gray-600">
        <thead class="bg-gray-50 border-b border-gray-100">
          <tr>
            <th class="px-6 py-4 font-semibold">Name</th>
            <th class="px-6 py-4 font-semibold">ID</th>
            <th class="px-6 py-4 font-semibold">Status</th>
            <th class="px-6 py-4 font-semibold text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="student in students" :key="student.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 font-medium text-gray-800">{{ student.name }}</td>
            <td class="px-6 py-4 text-xs font-mono text-gray-500">#{{ student.id }}</td>
            <td class="px-6 py-4">
              <span class="bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs">Encoded</span>
            </td>
            <td class="px-6 py-4 text-right space-x-2">
              <button @click="openEditModal(student)" class="text-blue-600 hover:underline">Edit</button>
              <button @click="deleteStudent(student.id)" class="text-red-600 hover:underline">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const showModal = ref(false)
const form = ref({
  name: '',
  file: null as File | null
})
const students = ref<any[]>([])
const currentStudentImages = ref<any[]>([])
const newImageInput = ref<HTMLInputElement | null>(null)

const fetchStudents = async () => {
    try {
        const { data } = await useFetch('http://localhost:8000/students/')
        if (data.value) {
            students.value = data.value as any[]
        }
    } catch (e) {
        console.error("Error fetching students", e)
    }
}

// Initial fetch
fetchStudents()

const isEditing = ref(false)
const editingId = ref<number | null>(null)

const openAddModal = () => {
    isEditing.value = false
    editingId.value = null
    form.value.name = ''
    form.value.file = null
    showModal.value = true
}

const openEditModal = (student: any) => {
    isEditing.value = true
    editingId.value = student.id
    form.value.name = student.name
    currentStudentImages.value = student.images || []
    showModal.value = true
}

const deleteImage = async (imageId: number) => {
    if (!confirm("Delete this training image?")) return
    try {
        await $fetch(`http://localhost:8000/images/${imageId}`, { method: 'DELETE' })
        // Refresh local list
        currentStudentImages.value = currentStudentImages.value.filter(img => img.id !== imageId)
        fetchStudents() // Refresh main list to sync consistency if needed
    } catch (e) {
        console.error("Error deleting image", e)
        alert("Failed to delete image")
    }
}

const uploadNewImage = async () => {
    const file = newImageInput.value?.files?.[0]
    if (!file || !editingId.value) return
    
    const formData = new FormData()
    formData.append('photo', file)
    
    try {
        const newImg = await $fetch(`http://localhost:8000/students/${editingId.value}/images`, {
            method: 'POST',
            body: formData
        })
        currentStudentImages.value.push(newImg)
        if (newImageInput.value) newImageInput.value.value = '' // Reset input
        alert("Image added!")
    } catch (e) {
        console.error("Error adding image", e)
        alert("Failed to add image. Ensure face is visible.")
    }
}

const deleteStudent = async (id: number) => {
    if (!confirm("Are you sure you want to delete this student?")) return
    
    try {
        await $fetch(`http://localhost:8000/students/${id}`, {
            method: 'DELETE'
        })
        fetchStudents()
    } catch (e) {
        console.error("Error deleting student", e)
        alert('Failed to delete student')
    }
}

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    form.value.file = target.files[0]
  } else {
    form.value.file = null
  }
}

const registerStudent = async () => {
  // Only for creating new student now. Editing name/images is handled differently.
  if (isEditing.value) {
      // Just update name if changed
      if (editingId.value) {
           await $fetch(`http://localhost:8000/students/${editingId.value}`, {
            method: 'PUT',
            body: new URLSearchParams({ name: form.value.name })
        }) 
      }
      showModal.value = false
      fetchStudents()
      return
  }

  if (!form.value.file) return
  
  const formData = new FormData()
  formData.append('name', form.value.name)
  formData.append('photo', form.value.file)
  
  try {
    await $fetch('http://localhost:8000/students/', {
        method: 'POST',
        body: formData
    })
    
    alert('Student Registered Successfully!')
    showModal.value = false
    form.value.name = ''
    form.value.file = null
    fetchStudents()
    
  } catch (e) {
    console.error("Error registering student", e)
    alert('Failed to register student.')
  }
}
</script>

