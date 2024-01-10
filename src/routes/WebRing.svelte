<script>
	import RecurseLogo from './RecurseLogo.svelte';
</script>

<div class="absolute bottom-2 left-2 w-36 border border-black shadow flex-col text-sm">
	<div class=" p-1 bg-green-400 hover:bg-green-500 border-b border-b-black text-center">
		<a
			id="rc-ring-home"
			data-rc-uuid="f53cf6e6-58ab-4be5-88ca-7ab639d7069d"
			href="https://ring.recurse.com/"
		>
			The <span class="h-4 w-4 inline-block"><RecurseLogo /></span> Webring</a
		>
	</div>
	<div class="flex w-full">
		<span class="px-1 bg-green-400 hover:bg-green-500 border-r border-r-black h-full"
			><a id="rc-ring-prev" href="https://ring.recurse.com/prev?id=17">&lt;&lt;</a>
		</span>
		<span
			class="px-1 bg-green-400 hover:bg-green-500 border-r border-r-black h-full grow text-center"
			><a id="rc-ring-rand" href="https://ring.recurse.com/rand">Random</a></span
		>
		<span class="px-1 bg-green-400 hover:bg-green-500 h-full"
			><a id="rc-ring-next" href="https://ring.recurse.com/next?id=17">&gt;&gt;</a></span
		>
	</div>
</div>
