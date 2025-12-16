<template>
  <div class="flex h-screen bg-gray-100 font-sans">
    <!-- Sidebar -->
    <aside class="w-64 bg-white shadow-md flex flex-col">
      <div class="p-6 border-b">
        <h1 class="text-2xl font-bold text-blue-600 flex items-center gap-2">
          <span>SmartAttend</span>
        </h1>
        <p class="text-xs text-gray-400 mt-1">IoT Attendance System</p>
      </div>
      
      <nav class="flex-1 p-4 space-y-2">
        <NuxtLink to="/" class="flex items-center gap-3 px-4 py-3 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-colors" active-class="bg-blue-50 text-blue-600 font-medium">
          Dashboard
        </NuxtLink>
        <NuxtLink to="/students" class="flex items-center gap-3 px-4 py-3 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-colors" active-class="bg-blue-50 text-blue-600 font-medium">
          Students
        </NuxtLink>
        <NuxtLink to="/attendance" class="flex items-center gap-3 px-4 py-3 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-colors" active-class="bg-blue-50 text-blue-600 font-medium">
          Attendance Log
        </NuxtLink>
      </nav>
      
      <div class="p-4 border-t text-xs text-gray-400 text-center">
        v2.0.0 Full Stack
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto">
      <header class="bg-white shadow-sm sticky top-0 z-10">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h2 class="text-lg font-semibold text-gray-800">
            <!-- Dynamic Page Title Logic could go here -->
            Admin Panel
          </h2>
          <div class="flex items-center gap-4">
            <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span class="text-sm text-gray-600">System Online</span>
          </div>
        </div>
      </header>
      
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <slot />
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Add any specific overrides here */
</style>
