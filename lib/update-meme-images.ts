require('dotenv').config({ path: '.env.local' })

import { supabase } from './supabase'

const dimensions = [
    '400x600',
    '500x700',
    '600x400',
    '700x500',
    '800x600',
    '600x800',
    '500x400',
    '400x500',
    '300x400',
    '400x300'
]

async function updateMemeImages() {
    // Fetch all memes
    const { data: memes, error: fetchError } = await supabase
        .from('memes')
        .select('id, image_url')

    if (fetchError) {
        console.error('Error fetching memes:', fetchError)
        return
    }

    if (!memes || memes.length === 0) {
        console.log('No memes found to update')
        return
    }

    console.log(`Found ${memes.length} memes to update`)

    // Update each meme with a random dimension
    for (let i = 0; i < memes.length; i++) {
        const meme = memes[i]
        const dimension = dimensions[i % dimensions.length]
        const newImageUrl = `https://placehold.co/${dimension}`

        const { error: updateError } = await supabase
            .from('memes')
            .update({ image_url: newImageUrl })
            .eq('id', meme.id)

        if (updateError) {
            console.error(`Error updating meme ${meme.id}:`, updateError)
        } else {
            console.log(`Updated meme ${meme.id} with dimension ${dimension}`)
        }
    }

    console.log('Update complete!')
}

// Run the update
updateMemeImages()
    .then(() => console.log('Script finished'))
    .catch((error) => console.error('Script failed:', error)) 