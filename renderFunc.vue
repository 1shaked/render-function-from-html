<script>
const imgComponent = () => import('./Image')
const videoComponent = () => import('./Video')
const audioComponent = () => import('./Audio')
const youtubeComponent = () => import('./Youtube')
const twitterComponent = () => import('./Twitter')
const facebookComponent = () => import('./Facebook')
const taboolaComponent = () => import('~/components/taboola')
export default {
  components: {
    'img-component': imgComponent,
    'video-component': videoComponent,
    'audio-component': audioComponent,
    'youtube-component': youtubeComponent,
    'twitter-component': twitterComponent,
    'facebook-component': facebookComponent,
    'taboola-component': taboolaComponent
  },
  computed: { ...mapState('articles', ['content']) },
  methods: {
    handleContent (content, h) {
      if (typeof content === 'string' || content instanceof String) {
        return content
      }
      if (Array.isArray(content) && content.length > 0) {
        return content.map((el) => {
          // console.log('%c currentElement: ' + el.tag + ' attrs: ' + el.attrs + ' content: ' + el.content, 'color: green; font-weight: bold')
          if (typeof el === 'string' || el instanceof String) {
            return el
          }
          const attrs = { attrs: { ...el.attrs } /* style: { order: '1' } */ }
          if (Array.isArray(el?.content) && el?.content?.length > 0) {
            return h(el.tag, {}, this.handleContent(el.content, h))
          }
          if (
            el.tag === 'iframe' &&
            el.attrs?.src?.includes('www.facebook.com')
          ) {
            return h('facebook-component', { props: { item: el.attrs.src } })
          }
          if (el.tag === 'img') {
            attrs.on = {
              click: (event) => { // add custom event
              }
            }
          }
          return h(el.tag || 'span', attrs, el.content)
        })
      }
      return ''
    }
  },
  render (createElement) {
    const content = [...this.content] // create copy to avoid error in reactive node
    return createElement('div', {}, this.handleContent(content, createElement))
  }
}
</script>