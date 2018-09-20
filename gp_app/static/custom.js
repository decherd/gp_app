$('#deleteModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget) // Button that triggered the modal
  var action = button.data('action')
  var delete_header = button.data('delete_header')
  var modal = $(this)
  modal.find('.modal-title').text(delete_header)
  modal.find('.modal-form-action').attr('action', action)
})
