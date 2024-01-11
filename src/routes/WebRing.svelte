<script lang="ts">
	import { onMount } from 'svelte';
	import RecurseLogo from './RecurseLogo.svelte';

	let showing = false;

	const hideOnClick = (event: MouseEvent) => {
		// showing = false;
		let element = event.target as HTMLElement;
		let found = false;

		while (element) {
			if (
				element.className &&
				typeof element.className === 'string' &&
				element.className?.includes('webringButton')
			) {
				found = true;
				break;
			}
			element = element.parentElement as HTMLElement;
		}
		console.log(found, element);
		if (!found) {
			showing = false;
		}
	};
	onMount(() => {
		window.addEventListener('click', hideOnClick);
		return () => {
			window.removeEventListener('click', hideOnClick);
		};
	});
</script>

<div class="relative h-7 w-7 webringButton">
	<button
		class="ml-2 inline-block px-1 w-7 h-7 bg-green-300 hover:bg-green-400 transition-colors border border-black"
		on:click={() => {
			showing = !showing;
		}}
	>
		<RecurseLogo />
	</button>

	{#if showing}
		<div class="ml-2 mt-[-4px] absolute w-36 border border-black shadow flex-col text-xs">
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
	{/if}
</div>
