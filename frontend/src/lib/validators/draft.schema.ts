import { z } from 'zod'

export const linkResponseSchema = z.object({
  method: z.enum(['GET', 'POST']),
  href: z.string(),
})

export const draftResponseSchema = z.object({
  thread_id: z.string(),
  status: z.enum(['draft', 'published', 'rejected']),
  approval_status: z.enum(['pending', 'approved', 'rejected']).nullable(),
  content: z.object({
    success: z.boolean(),
    error: z.string().nullable(),
    data: z.object({
      status: z.string(),
      approval_status: z.string().nullable(),
      platforms: z.object({
        facebook: z.object({
          generated: z.literal(true),
          post: z.string(),
          hashtags: z.array(z.string()),
          images: z.array(z.string()),
        }).optional(),
        instagram: z.object({
          generated: z.literal(true),
          caption: z.string(),
          hashtags: z.array(z.string()),
          images: z.array(z.string()),
        }).optional(),
      }),
    }),
  }),
  _links: z.record(linkResponseSchema),
})
